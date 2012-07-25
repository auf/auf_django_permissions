# encoding: utf-8

import itertools
import re
import urlparse

from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.db.models import Q
from django.shortcuts import render
from django.utils.importlib import import_module


# Roles and role providers

class Role(object):
    """
    Base class for roles.

    Doesn't give any permission.
    """

    def has_perm(self, perm):
        """
        Checks if this role gives the permission ``perm``.

        Returns True if it does, False if it doesn't.
        """
        return False

    def get_filter_for_perm(self, perm, model):
        """
        Returns a filter for instances of ``model`` for which this roles
        grants permission ``perm``.

        If the permission is granted on all instances of the model, the
        method returns True.

        If the permission is granted only on some instances of the model, the
        method returns a Q object that selects only those instances.

        If the permission is granted on no instances of the model, the
        method return False.
        """
        return False


def get_role_providers():
    """
    Gathers the role providers configured in the settings.
    """
    global _role_providers
    if _role_providers is None:
        _role_providers = []
        for path in getattr(settings, 'ROLE_PROVIDERS', []):
            module_path, sep, provider_name = path.rpartition('.')
            try:
                module = import_module(module_path)
            except ImportError, e:
                raise ImproperlyConfigured(
                    "Error importing role provider %s: %s" % path, e
                )
            try:
                provider = getattr(module, provider_name)
            except AttributeError:
                raise ImproperlyConfigured(
                    'Module "%s" does not define a role provider named "%s"' %
                    (module_path, provider_name)
                )
            _role_providers.append(provider)
    return _role_providers
_role_providers = None


def get_roles(user):
    """
    Returns the roles given to a user.
    """
    return list(itertools.chain.from_iterable(
        p(user) for p in get_role_providers()
    ))


# Permission checking

def user_has_perm(user, perm, obj=None):
    """
    Checks whether a user has the given permission.
    """
    roles = get_roles(user)
    if obj is None:
        return any(role.has_perm(perm) for role in roles)
    else:
        for role in roles:
            q = role.get_filter_for_perm(perm, type(obj))
            if q is True or (isinstance(q, Q) and qeval(obj, q)):
                return True
        return False


def queryset_with_perm(queryset, user, perm):
    """
    Filters ``queryset``, leaving only objects on which ``user`` has the
    permission ``perm``.
    """
    # Special case: superusers have all permissions on all objects.
    if user.is_superuser:
        return queryset

    roles = get_roles(user)
    query = None
    for role in roles:
        q = role.get_filter_for_perm(perm, queryset.model)
        if q is True:
            return queryset
        elif q is not False:
            if query:
                query |= q
            else:
                query = q
    if query:
        return queryset.filter(query)
    else:
        return queryset.none()


def qeval(obj, q):
    """
    Evaluates a Q object on an instance of a model.
    """

    # Evaluate all children
    for child in q.children:
        if isinstance(child, Q):
            result = qeval(child)
        else:
            filter, value = child
            bits = filter.split('__')
            path = bits[:-1]
            lookup = bits[-1]
            for attr in path:
                obj = getattr(obj, attr)
            if lookup == 'exact':
                result = obj == value
            elif lookup == 'iexact':
                result = obj.lower() == value.lower()
            elif lookup == 'contains':
                result = value in obj
            elif lookup == 'icontains':
                result = value.lower() in obj.lower()
            elif lookup == 'in':
                result = obj in value
            elif lookup == 'gt':
                result = obj > value
            elif lookup == 'gte':
                result = obj >= value
            elif lookup == 'lt':
                result = obj < value
            elif lookup == 'lte':
                result = obj <= value
            elif lookup == 'startswith':
                result = obj.startswith(value)
            elif lookup == 'istartswith':
                result = obj.lower().istartswith(value.lower())
            elif lookup == 'endswith':
                result = obj.lower().iendswith(value.lower())
            elif lookup == 'range':
                result = value[0] <= obj <= value[1]
            elif lookup == 'year':
                result = obj.year == value
            elif lookup == 'month':
                result = obj.month == value
            elif lookup == 'day':
                result = obj.day == value
            elif lookup == 'week_day':
                result = (obj.weekday() + 1) % 7 + 1 == value
            elif lookup == 'isnull':
                result = (obj is None) if value else (obj is not None)
            elif lookup == 'search':
                raise NotImplementedError(
                    'qeval does not implement "__search"'
                )
            elif lookup == 'regex':
                result = bool(re.search(value, obj))
            elif lookup == 'iregex':
                result = bool(re.search(value, obj, re.I))
            else:
                obj = getattr(obj, lookup)
                result = obj == value

        # See if we can shortcut
        if result and q.connector == Q.OR:
            return True
        if not result and q.connector == Q.AND:
            return False

    # We could'nt shortcut
    if q.connector == Q.OR:
        result = False
    if q.connector == Q.AND:
        result = True

    # Negate if necessary
    if q.negated:
        return not result
    else:
        return result


# Authentication backend

class AuthenticationBackend(object):
    supports_anonymous_user = True
    supports_inactive_user = True
    supports_object_permissions = True

    def has_perm(self, user, perm, obj=None):
        return user_has_perm(user, perm, obj)

    def has_module_perms(self, user, package_name):
        return user_has_perm(user, package_name)

    def authenticate(self, username=None, password=None):
        # We don't authenticate
        return None

    def get_user(self, user_id):
        # We don't authenticate
        return None


# View protection and PermissionDenied management

def require_permission(user, perm, obj=None):
    if not user.has_perm(perm, obj):
        raise PermissionDenied


class PermissionDeniedMiddleware(object):

    def process_exception(self, request, exception):
        if isinstance(exception, PermissionDenied):
            if request.user.is_anonymous():

                # Code de redirection venant de
                # django.contrib.auth.decorators.permission_required()
                path = request.build_absolute_uri()
                login_url = settings.LOGIN_URL
                # If the login url is the same scheme and net location then
                # just use the path as the "next" url.
                login_scheme, login_netloc = urlparse.urlparse(login_url)[:2]
                current_scheme, current_netloc = urlparse.urlparse(path)[:2]
                if ((not login_scheme or login_scheme == current_scheme) and
                    (not login_netloc or login_netloc == current_netloc)):
                    path = request.get_full_path()
                return redirect_to_login(path, login_url, 'next')
            else:
                return render(request, '403.html')
        else:
            return None

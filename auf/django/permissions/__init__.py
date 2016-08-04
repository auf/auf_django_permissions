# encoding: utf-8

import itertools
import re
import urlparse

from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.db.models import Q, Manager
from django.http import HttpResponseForbidden
from django.template.loader import render_to_string
try:
    from importlib import import_module
except ImportError:  # python 2.6
    from django.utils.importlib import import_module


# Roles and role providers

class Role(object):
    """
    Base class for roles.

    Doesn't give any permission.
    """

    def has_perm(self, perm, obj=None):
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
    if any(role.has_perm(perm, obj) for role in roles):
        return True
    elif obj is not None:
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
    def q_getattr(x, attr):
        y = getattr(x, attr)
        if y is None:
            return
        elif isinstance(y, Manager):
            for z in y.all():
                yield z
        else:
            yield y

    # Evaluate all children
    for child in q.children:
        if isinstance(child, Q):
            result = qeval(obj, child)
        else:
            filter, value = child
            bits = filter.split('__')
            path = bits[:-1]
            lookup = bits[-1]

            # Traverse the attribute path and find all candidate values
            candidates = [obj]
            for attr in path:
                candidates = list(itertools.chain.from_iterable(
                    q_getattr(x, attr) for x in candidates
                ))

            if lookup == 'exact':
                result = any(x == value for x in candidates)
            elif lookup == 'iexact':
                result = any(x.lower() == value.lower() for x in candidates)
            elif lookup == 'contains':
                result = any(value in x for x in candidates)
            elif lookup == 'icontains':
                result = any(value.lower() in x.lower() for x in candidates)
            elif lookup == 'in':
                result = any(x in value for x in candidates)
            elif lookup == 'gt':
                result = any(x > value for x in candidates)
            elif lookup == 'gte':
                result = any(x >= value for x in candidates)
            elif lookup == 'lt':
                result = any(x < value for x in candidates)
            elif lookup == 'lte':
                result = any(x <= value for x in candidates)
            elif lookup == 'startswith':
                result = any(x.startswith(value) for x in candidates)
            elif lookup == 'istartswith':
                result = any(
                    x.lower().istartswith(value.lower())
                    for x in candidates
                )
            elif lookup == 'endswith':
                result = any(
                    x.lower().iendswith(value.lower()) for x in candidates
                )
            elif lookup == 'range':
                result = any(value[0] <= x <= value[1] for x in candidates)
            elif lookup == 'year':
                result = any(x.year == value for x in candidates)
            elif lookup == 'month':
                result = any(x.month == value for x in candidates)
            elif lookup == 'day':
                result = any(x.day == value for x in candidates)
            elif lookup == 'week_day':
                result = any(
                    (x.weekday() + 1) % 7 + 1 == value for x in candidates
                )
            elif lookup == 'isnull':
                if value:
                    return not candidates
                else:
                    return bool(candidates)
            elif lookup == 'search':
                raise NotImplementedError(
                    'qeval does not implement "__search"'
                )
            elif lookup == 'regex':
                result = any(bool(re.search(value, x)) for x in candidates)
            elif lookup == 'iregex':
                result = any(
                    bool(re.search(value, x, re.I)) for x in candidates
                )
            else:
                candidates = list(itertools.chain.from_iterable(
                    q_getattr(x, lookup) for x in candidates
                ))
                result = any(x == value for x in candidates)

        # See if we can shortcut
        if (result and q.connector == Q.OR) \
           or (not result and q.connector == Q.AND):
            break

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
                return HttpResponseForbidden(render_to_string('403.html'))
        else:
            return None

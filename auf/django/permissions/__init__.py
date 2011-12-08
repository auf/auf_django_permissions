from collections import defaultdict

class Rules(object):

    def __init__(self):
        self.tests = defaultdict(list)
        self.qs = defaultdict(list)
        self.test_qs = defaultdict(list)

    def clear(self):
        self.tests.clear()
        self.qs.clear()
        self.test_qs.clear()

    def add(self, perm, cls=None, test=None, q=None):
        if test:
            self.tests[(perm, cls)].append(test)
        if q:
            self.qs[(perm, cls)].append(q)
            if not test:
                self.test_qs[(perm, cls)].append(q)

    def test(self, user, perm, obj=None):
        if obj is None:
            tests = self.tests[(perm, None)]
            return any(test(user) for test in tests)

        cls = type(obj)
        tests = self.tests[(perm, cls)]
        if any(test(user, obj) for test in tests):
            return True
        qs = self.test_qs[(perm, cls)]
        if qs:
            q = reduce(lambda x, y: x | y, (q(user) for q in qs))
            if cls._default_manager.filter(q).filter(pk=obj.pk).exists():
                return True
        return False

    def get_q(self, user, perm, cls):
        qs = self.qs[(perm, cls)]
        return reduce(lambda x, y: x | y, (q(user) for q in qs)) if qs else None

allow_rules = Rules()
deny_rules = Rules()

def allow(perm, cls=None, test=None, q=None):
    allow_rules.add(perm, cls, test, q)

def deny(perm, cls=None, test=None, q=None):
    deny_rules.add(perm, cls, test, q)

def user_has_perm(user, perm, obj=None):
    return not deny_rules.test(user, perm, obj) and allow_rules.test(user, perm, obj)

def filter(user, perm, queryset):
    deny_q = deny_rules.get_q(user, perm, queryset.model)
    if deny_q:
        queryset = queryset.exclude(deny_q)
    allow_q = allow_rules.get_q(user, perm, queryset.model)
    if allow_q:
        queryset = queryset.filter(allow_q)
    else:
        queryset = queryset.none()
    return queryset

def clear_rules():
    allow_rules.clear()
    deny_rules.clear()

def autodiscover():
    """
    Auto-discover INSTALLED_APPS permissions.py modules and fail silently when
    not present. This forces an import on them to register permission rules.
    This is freely adapted from django.contrib.admin.autodiscover()
    """

    import copy
    from django.conf import settings
    from django.utils.importlib import import_module
    from django.utils.module_loading import module_has_submodule

    for app in settings.INSTALLED_APPS:
        mod = import_module(app)
        # Attempt to import the app's permissions module.
        try:
            import_module('%s.permissions' % app)
        except:
            # Decide whether to bubble up this error. If the app just
            # doesn't have a permissions module, we can ignore the error
            # attempting to import it, otherwise we want it to bubble up.
            if module_has_submodule(mod, 'permissions'):
                raise

# encoding: utf-8

from collections import defaultdict


class Predicate(object):
    """
    Wrapper pour une fonction ``f(user, obj, cls)``.

    Le paramètre ``user`` est l'utilisateur pour lequel la permission est testée.

    Si le prédicat est testé sur un seul objet, cet objet est passé dans
    le paramètre ``obj`` et le paramètre ``cls`` est ``None``. Inversement,
    si le prédicat sert à filtrer un queryset, le modèle du queryset est
    passé dans le paramètre ``cls`` et le paramètre ``obj`` est ``None``.

    La fonction peut retourner un booléen ou un objet ``Q``. Un booléen
    indique si le test a passé ou pas. Un objet ``Q`` indique les filtres à
    appliquer pour ne garder que les objets qui passent le test. Si un objet
    ``Q`` est retourné lors d'un test sur un seul objet, le test retournera
    un booléen indiquant si l'objet satisfait au filtre.

    Les prédicats peuvent être combinés à l'aide des opérateurs booléens
    ``&``, ``|`` et ``~``.
    """

    def __init__(self, func_or_value):
        """
        On peut initialiser un prédicat avec une fonction ayant la signature
        ``f(user, obj, cls)`` ou avec une valeur constante.
        """
        if callable(func_or_value):
            self.func = func_or_value
        else:
            self.func = lambda user, obj, cls: func_or_value

    def __call__(self, user, obj=None, cls=None):
        """
        Appelle la fonction encapsulée.
        """
        return self.func(user, obj, cls)

    def __and__(self, other):
        def func(user, obj, cls):
            my_result = self(user, obj, cls)
            if my_result is False:
                return False
            other_result = other(user, obj, cls)
            if my_result is True:
                return other_result
            elif other_result is True:
                return my_result
            else:
                return my_result & other_result
        return Predicate(func)

    def __or__(self, other):
        def func(user, obj, cls):
            my_result = self(user, obj, cls)
            if my_result is True:
                return True
            other_result = other(user, obj, cls)
            if my_result is False:
                return other_result
            elif other_result is False:
                return my_result
            else:
                return my_result | other_result
        return Predicate(func)

    def __invert__(self):
        def func(user, obj, cls):
            result = self(user, obj, cls)
            if isinstance(result, bool):
                return not result
            else:
                return ~result
        return Predicate(func)


class Rules(object):

    def __init__(self, allow_default=None, deny_default=None):
        self.allow_rules = defaultdict(lambda: allow_default or Predicate(False))
        self.deny_rules = defaultdict(lambda: deny_default or Predicate(False))

    def allow(self, perm, cls, predicate):
        if not isinstance(predicate, Predicate):
            raise TypeError("the third argument to allow() must be a Predicate")
        self.allow_rules[(perm, cls)] |= predicate

    def deny(self, perm, cls, predicate):
        if not isinstance(predicate, Predicate):
            raise TypeError("the third argument to deny() must be a Predicate")
        self.deny_rules[(perm, cls)] |= predicate

    def predicate_for_perm(self, perm, cls):
        return self.allow_rules[(perm, cls)] & ~self.deny_rules[(perm, cls)]

    def user_has_perm(self, user, perm, obj):
        result = self.predicate_for_perm(perm, obj.__class__)(user, obj)
        if isinstance(result, bool):
            return result
        else:
            return obj._default_manager.filter(pk=obj.pk).filter(result).exists()

    def filter_queryset(self, user, perm, queryset):
        result = self.predicate_for_perm(perm, queryset.model)(user, cls=queryset.model)
        if result is True:
            return queryset
        elif result is False:
            return queryset.none()
        else:
            return queryset.filter(result)

    def clear():
        self.allow_rules.clear()
        self.deny_rules.clear()


class AuthenticationBackend(object):
    supports_anonymous_user = True
    supports_inactive_user = True
    supports_object_permissions = True
    rules = None

    def has_perm(self, user, perm, obj=None):
        if self.rules is None or obj is None:
            return False
        return self.rules.user_has_perm(user, perm, obj)

    def authenticate(self, username=None, password=None):
        # We don't authenticate
        return None

    def get_user(self, user_id):
        # We don't authenticate
        return None

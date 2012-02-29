# encoding: utf-8

"""
Builtin predicates.
"""

from auf.django.permissions import Predicate, get_rules


def has_global_perm(perm):
    def p(user):
        return user.has_perm(perm)
    return Predicate(p)

def has_object_perm(perm):
    def p(user, obj, cls):
        return get_rules().predicate_for_perm(perm, cls or obj.__class__)(user, obj, cls)
    return Predicate(p)

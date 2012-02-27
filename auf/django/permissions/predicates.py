# encoding: utf-8

"""
Builtin predicates.
"""

from auf.django.permissions import Predicate, predicate_for_perm, predicate_generator


def has_global_perm(perm):
    def p(user, obj, cls):
        return user.has_perm(perm)
    return Predicate(p)

def has_object_perm(perm):
    def p(user, obj, cls):
        return predicate_for_perm(perm, model or obj.__class__)(user, obj, model)
    return Predicate(p)

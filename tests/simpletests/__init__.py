from __future__ import absolute_import

from auf.django.permissions import Role
from django.db.models import Q

from tests.simpletests.models import Food


def role_provider(user):
    if user.username == 'alice':
        return [VegetarianRole(user)]
    elif user.username == 'bob':
        return [HippieRole()]
    else:
        return []


class VegetarianRole(Role):

    def __init__(self, user):
        self.user = user

    def get_filter_for_perm(self, perm, model):
        if model is Food:
            if perm == 'eat':
                return Q(is_meat=False)
            elif perm == 'buy':
                return True
            elif perm == 'throw':
                return False
            elif perm == 'give':
                return Q(is_meat=True) | Q(name__contains='canned')
            elif perm == 'paint':
                return Q(owner__username__startswith='a')
        return False


class HippieRole(Role):

    def has_perm(self, perm):
        return perm in ('eat', 'pray', 'love')

from __future__ import absolute_import

from auf.django.permissions import Role
from django.db.models import Q

from tests.simpletests.models import Food


def role_provider(user):
    if user.username == 'alice':
        return [VegetarianRole()]
    elif user.username == 'bob':
        return [HippieRole()]
    else:
        return []


class VegetarianRole(Role):

    def get_filter_for_perm(self, perm, model):
        if model is Food:
            if perm == 'eat':
                return Q(is_meat=False)
            elif perm == 'buy':
                return True
            elif perm == 'throw':
                return False
        return False


class HippieRole(Role):

    def has_perm(self, perm):
        return perm in ('eat', 'pray', 'love')

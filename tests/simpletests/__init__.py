from __future__ import absolute_import

from auf.django.permissions import Role
from django.db.models import Q

from tests.simpletests.models import Food


def role_provider(user):
    if user.username == 'alice':
        return [VegetarianRole()]
    else:
        return []


class VegetarianRole(Role):

    def has_perm(self, perm):
        return perm in ('eat', 'pray', 'love')

    def get_filter_for_perm(self, perm, model):
        if model is Food and perm == 'eat':
            return Q(is_meat=False)
        return False

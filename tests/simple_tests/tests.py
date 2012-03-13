from __future__ import absolute_import

from django.contrib.auth.models import User, Group
from django.utils import unittest


class GlobalPermsTestCase(unittest.TestCase):

    def setUp(self):
        self.alice = User.objects.create_user('alice', 'alice@example.com')

    def test_add_remove_user_permissions(self):
        self.alice.global_permissions.add_permission('open_door')
        self.assertSetEqual(
            self.alice.global_permissions.get_permissions(),
            set(['open_door'])
        )
        self.alice.global_permissions.add_permission('close_door')
        self.assertSetEqual(
            self.alice.global_permissions.get_permissions(),
            set(['open_door', 'close_door'])
        )
        self.alice.global_permissions.remove_permission('open_door')
        self.assertSetEqual(
            self.alice.global_permissions.get_permissions(),
            set(['close_door'])
        )
        self.alice.global_permissions.add_permission('close_door')
        self.assertSetEqual(
            self.alice.global_permissions.get_permissions(),
            set(['close_door'])
        )
        self.alice.global_permissions.remove_permission('open_door')
        self.assertSetEqual(
            self.alice.global_permissions.get_permissions(),
            set(['close_door'])
        )

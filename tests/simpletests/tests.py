from __future__ import absolute_import

from django.contrib.auth.models import User
from django.test import TransactionTestCase

from tests.simpletests.models import Food


class HasPermTestCase(TransactionTestCase):

    def setUp(self):
        self.alice = User.objects.create(username='alice')
        self.bob = User.objects.create(username='bob')
        self.superman = User.objects.create(
            username='superman', is_superuser=True
        )
        self.carrot = Food.objects.create(
            owner=self.alice, name=u'carrot', is_meat=False
        )
        self.celery = Food.objects.create(name=u'celery', is_meat=False)
        self.steak = Food.objects.create(name=u'steak', is_meat=True)
        self.soup = Food.objects.create(name=u'canned soup', is_meat=False)

    def test_global_permissions(self):
        self.assertTrue(self.bob.has_perm('eat'))
        self.assertFalse(self.bob.has_perm('sleep'))
        self.assertFalse(self.alice.has_perm('eat'))

    def test_object_permissions(self):
        self.assertTrue(self.alice.has_perm('eat', self.carrot))
        self.assertFalse(self.alice.has_perm('throw', self.carrot))
        self.assertFalse(self.alice.has_perm('eat', self.steak))
        self.assertTrue(self.alice.has_perm('buy', self.steak))
        self.assertFalse(self.alice.has_perm('give', self.carrot))
        self.assertTrue(self.alice.has_perm('paint', self.carrot))
        self.assertFalse(self.alice.has_perm('paint', self.steak))

    def test_queryset_filtering(self):
        self.assertEqual(
            set(Food.objects.with_perm(self.alice, 'eat')),
            set([self.carrot, self.celery, self.soup])
        )
        self.assertEqual(
            set(Food.objects.with_perm(self.alice, 'throw')),
            set()
        )
        self.assertEqual(
            set(Food.objects.with_perm(self.alice, 'buy')),
            set(Food.objects.all())
        )
        self.assertEqual(
            set(Food.objects.with_perm(self.bob, 'eat')),
            set()
        )

    def test_superuser_queryset_filtering(self):
        self.assertEqual(
            set(Food.objects.with_perm(self.superman, 'eat')),
            set(Food.objects.all())
        )

from __future__ import absolute_import

from django.contrib.auth.models import User
from django.test import TransactionTestCase

from tests.simpletests.models import Food


class HasPermTestCase(TransactionTestCase):

    def setUp(self):
        self.alice = User.objects.create(username='alice')
        self.carrot = Food.objects.create(is_meat=False)
        self.celery = Food.objects.create(is_meat=False)
        self.steak = Food.objects.create(is_meat=True)

    def test_global_permissions(self):
        self.assertTrue(self.alice.has_perm('eat'))
        self.assertFalse(self.alice.has_perm('sleep'))

    def test_object_permissions(self):
        self.assertTrue(self.alice.has_perm('eat', self.carrot))
        self.assertFalse(self.alice.has_perm('eat', self.steak))

    def test_queryset_filtering(self):
        actual = Food.objects.with_perm(self.alice, 'eat') \
                .values_list('id', flat=True)
        expected = [x.id for x in (self.carrot, self.celery)]
        self.assertItemsEqual(actual, expected)

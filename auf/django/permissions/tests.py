import re

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.http import HttpRequest
from django.template import Template, RequestContext
from django.utils import unittest
from django.utils.text import normalize_newlines

import auf.django.permissions as perms


class Food(models.Model):
    name = models.CharField(max_length=100)
    allergic_users = models.ManyToManyField(User, related_name='allergies')

    def __repr__(self):
        return "<Food %r>" % self.name
    

class FoodTestCase(unittest.TestCase):

    def setUp(self):
        self.alice = User.objects.create_user('alice', 'alice@example.com')
        self.bob = User.objects.create_user('bob', 'bob@example.com')
        self.apple = Food.objects.create(name='apple')
        self.banana = Food.objects.create(name='banana')
        self.banana.allergic_users.add(self.alice)

    def tearDown(self):
        self.alice.delete()
        self.bob.delete()
        self.apple.delete()
        self.banana.delete()
        perms.clear_rules()


class RulesTestCase(FoodTestCase):

    def test_global_perms(self):
        perms.allow('sing', test=lambda user: user is self.alice)
        self.assertTrue(self.alice.has_perm('sing'))
        self.assertFalse(self.alice.has_perm('dance'))

    def test_global_deny(self):
        perms.allow('eat', test=lambda user: True)
        perms.deny('eat', test=lambda user: user is self.bob)
        self.assertTrue(self.alice.has_perm('eat'))
        self.assertFalse(self.bob.has_perm('eat'))

    def test_object_perms(self):
        perms.allow('eat', Food, test=lambda user, obj: obj not in user.allergies.all())
        self.assertTrue(self.alice.has_perm('eat', self.apple))
        self.assertFalse(self.alice.has_perm('eat', self.banana))

    def test_object_deny(self):
        perms.allow('eat', Food, test=lambda user, obj: True)
        perms.deny('eat', Food, test=lambda user, obj: obj in user.allergies.all())
        self.assertTrue(self.alice.has_perm('eat', self.apple))
        self.assertFalse(self.alice.has_perm('eat', self.banana))

    def test_no_rules(self):
        self.assertFalse(self.alice.has_perm('climb'))
        perms.allow('eat', Food, test=lambda user, obj: True)
        self.assertTrue(self.alice.has_perm('eat', self.apple))
        self.assertFalse(self.alice.has_perm('eat', self.bob))

    def test_q_rules(self):
        perms.allow('eat', Food, q=lambda user: ~Q(allergic_users=user))
        self.assertListEqual(list(perms.filter(self.alice, 'eat', Food.objects.all())),
                             [self.apple])
        self.assertListEqual(list(perms.filter(self.bob, 'eat', Food.objects.all())),
                             [self.apple, self.banana])
        self.assertTrue(self.alice.has_perm('eat', self.apple))
        self.assertFalse(self.alice.has_perm('eat', self.banana))

class TemplateTagsTestCase(FoodTestCase):

    def setUp(self):
        FoodTestCase.setUp(self)
        perms.allow('eat', Food, 
                    test=lambda user, obj: obj not in user.allergies.all(),
                    q=lambda user: ~Q(allergic_users=user))
        perms.allow('throw', Food, test=lambda user, obj: True)

    def test_ifhasperm(self):
        template = Template("""{% load permissions %}
{% for fruit in food %}
{% ifhasperm "eat" fruit %}
Eat the {{ fruit.name }}
{% else %}
Don't eat the {{ fruit.name }}
{% endifhasperm %}
{% endfor %}""")
        request = HttpRequest()
        request.user = self.alice
        context = RequestContext(request, {'food': Food.objects.all()})
        self.assertRegexpMatches(template.render(context).strip(),
                                 r'\s+'.join([
                                     "Eat the apple",
                                     "Don't eat the banana"
                                 ])
                                )

    def test_withperms(self):
        template = Template("""{% load permissions %}
{% for fruit in food %}
{% withperms fruit as fruit_perms %}
Eat {{ fruit.name }}: {{ fruit_perms.eat|yesno }}
Throw {{ fruit.name }}: {{ fruit_perms.throw|yesno }}
Smoke {{ fruit.name }}: {{ fruit_perms.smoke|yesno }}
{% endwithperms %}
{% endfor %}""")
        request = HttpRequest()
        request.user = self.alice
        context = RequestContext(request, {'food': Food.objects.all()})
        self.assertRegexpMatches(template.render(context).strip(),
                                 r'\s+'.join([
                                     "Eat apple: yes",
                                     "Throw apple: yes",
                                     "Smoke apple: no",
                                     "Eat banana: no",
                                     "Throw banana: yes",
                                     "Smoke banana: no"
                                 ])
                                )

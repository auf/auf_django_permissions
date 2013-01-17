from django.contrib.auth.models import User
from django.db import models


class Food(models.Model):
    owner = models.ForeignKey(User, null=True, blank=True)
    name = models.CharField(max_length=255)
    is_meat = models.BooleanField()

    def __unicode__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(max_length=255)
    ingredients = models.ManyToManyField(Food)

    def __unicode__(self):
        return self.name

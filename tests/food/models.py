from django.contrib.auth.models import User
from django.db import models


class Food(models.Model):
    name = models.CharField(max_length=100)
    allergic_users = models.ManyToManyField(User, related_name='allergies')

    def __repr__(self):
        return "<Food %r>" % self.name

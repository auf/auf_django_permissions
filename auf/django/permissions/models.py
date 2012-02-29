from django.contrib.auth.models import User, Group
from django.db import models


class GlobalUserPermission(models.Model):
    user = models.ForeignKey(User, related_name='global_permissions')
    codename = models.CharField(max_length=100)

class GlobalGroupPermission(models.Model):
    group = models.ForeignKey(Group, related_name='global_permissions')
    codename = models.CharField(max_length=100)

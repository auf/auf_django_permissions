from django.contrib.auth.models import User, Group
from django.db import models


class GlobalPermissionManager(models.Manager):

    def add_permission(self, codename):
        self.get_or_create(codename=codename)

    def remove_permission(self, codename):
        self.filter(codename=codename).delete()

    def get_permissions(self):
        return set(p.codename for p in self.all())


class GlobalUserPermission(models.Model):
    user = models.ForeignKey(User, related_name='global_permissions')
    codename = models.CharField(max_length=100)
    objects = GlobalPermissionManager()


class GlobalGroupPermission(models.Model):
    group = models.ForeignKey(Group, related_name='global_permissions')
    codename = models.CharField(max_length=100)
    objects = GlobalPermissionManager()

# encoding: utf-8

from django.db.models import Manager
from django.db.models.query import QuerySet

from auf.django.permissions import queryset_with_perm


# Add nice methods to the Django Queryset

def _manager_with_perm(manager, *args, **kwargs):
    try:
        return manager.get_query_set().with_perm(*args, **kwargs)
    except AttributeError:  # django 1.8
        return manager.get_queryset().with_perm(*args, **kwargs)


Manager.with_perm = _manager_with_perm
QuerySet.with_perm = queryset_with_perm

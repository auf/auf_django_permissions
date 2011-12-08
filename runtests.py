#!/usr/bin/python2

from django.conf import settings
from django.core.management import call_command

settings.configure(
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:'
        }
    },
    INSTALLED_APPS=(
        'django.contrib.auth', 
        'django.contrib.contenttypes',
        'auf.django.permissions'
    ),
    AUTHENTICATION_BACKENDS=(
        'auf.django.permissions.backends.AuthenticationBackend',
    ),
    TEMPLATE_LOADERS=(
        'django.template.loaders.app_directories.Loader',
    ),
    TEMPLATE_CONTEXT_PROCESSORS=(
        'django.core.context_processors.request',
    )
)
call_command('test', 'permissions')

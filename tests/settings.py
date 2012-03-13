DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'auf.django.permissions',
    'tests.food',
    'tests.simple_tests'
)

AUTHENTICATION_BACKENDS = (
    'auf.django.permissions.AuthenticationBackend',
)

TEMPLATE_LOADERS = (
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.request',
)

AUF_PERMISSIONS_RULES = 'tests.permissions.rules'

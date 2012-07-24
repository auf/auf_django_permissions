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
    'tests.simpletests',
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

ROLE_PROVIDERS = (
    'tests.simpletests.role_provider',
)

SECRET_KEY = 'not-very-secret'

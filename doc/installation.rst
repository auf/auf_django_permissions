.. _installation:

Installation
============

Installez l'app dans votre configuration Django::

    INSTALLED_APPS = (
        ...
        'auf.django.permissions',
        ...
    )

Puis, configurez le backend d'authentification::

    AUTHENTICATION_BACKENDS = (
        ...
        'auf.django.permissions.AuthenticationBackend',
        ...
    )

Et le middleware pour gérer les échecs d'autorisation::

    MIDDLEWARE_CLASSES = (
        ...
        'auf.django.permissions.PermissionDeniedMiddleware',
        ...
    )

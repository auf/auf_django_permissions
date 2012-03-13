Installation
============

Installez l'app dans votre configuration Django::

    INSTALLED_APPS = {
        ...
        'auf.django.permissions',
        ...
    }

Puis, configurez le backend d'authentification::

    AUTHENTICATION_BACKENDS = (
        ...
        'auf.django.permissions.AuthenticationBackend',
        ...
    )

Vous devez maintenant créer un module qui contiendra vos règles d'accès. Par
exemple: ``monprojet/permissions.py``. Au départ, il contiendra un jeu de règles
vide::

    from auf.django.permissions import Rules

    rules = Rules()

Vous pouvez maintenant retourner dans votre configuration Django et indiquer où
se trouve votre jeu de règles::

    AUF_PERMISSIONS_RULES = 'monprojet.permissions.rules'

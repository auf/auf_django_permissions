Utilisation
===========

Permissions globales
--------------------

``auf.django.permissions`` ajoute un système de permissions globales distinct de
celui de Django. C'est un système très simple qui permet d'associer globalement
une permission à un utilisateur. Ces permissions globales sont identifiées par
une chaîne de caractères et, contrairement aux permissions Django, ne sont
associées ni à une app, ni à un modèle.

Ces permissions globales sont disponibles à partir du manager
``global_permissions`` des objets ``User`` et ``Group`` de Django. Les objets
gérés par ce manager ont un seul attribut, ``codename``, qui contient le nom de
la permission à donner à l'utilisateur ou au groupe. On gère donc les
permissions globales de la façon suivante::

    user = User.objects.get(username='alice')

    # Ajouter une permission
    user.global_permissions.create(codename='monapp.voir_les_documents_confidentiels')

    # Supprimer une permission
    user.global_permissions.filter(codename='monapp.voir_les_fichiers_top_secret').delete()

    # Afficher une liste de toutes les permissions
    for p in user.global_permissions.all():
        print p.codename



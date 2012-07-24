Utilisation
===========

Une fois qu'on a défini nos rôles, :mod:`auf.django.permissions` nous offre
toutes sortes de façons d'en faire usage.

Système de permissions de Django
--------------------------------

Grâce au backend d'authentification configuré à la section
:ref:`installation`, les permissions données par les rôles seront disponibles
dans le système de permissions de Django. On pourra donc vérifier si un
utilisateur a la permission de lire le journal::

    if user.has_perm('lire_le_journal'):
        ...

ou s'il a la permission d'éditer un article en particulier::

    if user.has_perm('editer', article):
        ...

Protection des vues
-------------------

:mod:`auf.django.permissions` offre une alternative au décorateur
:func:`permission_required` de Django. Au lieu de décorer la vue à protéger, on
appelera la fonction :func:`require_permission`.

.. function:: require_permission(user, perm, obj=None)

    Vérifie si *user* a la permission *perm* pour l'objet *obj*. Si *obj* n'est
    pas donné, vérifie simplement si *user* a la permission globale *perm*. Si
    l'utilisateur n'a pas la permission demandée, l'exception
    :exc:`django.core.exceptions.PermissionDenied` est lancée.

Lorsque :func:`require_permission` refuse l'accès, l'exception
:exc:`PermissionDenied` est lancée, ce qui fait réagir le
middleware :class:`PermissionDeniedMiddleware` configuré à la section
:ref:`installation`. Ce middleware réagit d'une des deux façons suivantes:

* Si l'utilisateur n'est pas connecté (anonyme), il redirige à la page de
  connexion définie par le *setting* ``LOGIN_URL``.
* Si l'utilisateur est connecté, il génère une page 403 en utilisant le template
  :file:`403.html`.

Filtrage des querysets
----------------------

:mod:`auf.django.permissions` ajoute la méthode ``with_perm(user, perm)``
aux managers et querysets de Django. Cette méthode filtre le queryset en ne
gardant que les objets pour lesquels *user* a la permission *perm*. Par exemple,
pour avoir une liste des articles qu'Alice peut éditer, on écrira simplement::

    Article.objects.with_perm(alice, 'editer')

Il est à noter que cette fonctionnalité n'est pas intégrée avec le système de
permissions de Django et que seules les permissions définies par des rôles
peuvent être utilisées.

Templates
---------

Puisque les permissions d':mod:`auf.django.permissions` sont intégrées dans le
système de permissions de Django, on peut se servir du *context processor*
standard de Django pour tester les permissions:

.. code-block:: django

    {% if perms.lire_le_journal %}
    ...
    {% endif %}

Pour que l'objet *perms* soit disponible, il faut que le *context processor*
soit enregistré dans les settings::

    TEMPLATE_CONTEXT_PROCESSORS = (
        'django.contrib.auth.context_processors.auth',
        ...
    )

Ce mécanisme fonctionne bien pour les permissions générales, mais pour les
permissions liées à un objet, il faut des mécanismes supplémentaires.
:mod:`auf.django.permissions` offre les *template tags* suivants:

{% ifhasperm *perm* *obj* %}
    Ce *template tag* exécute son contenu seulement si l'utilisateur courant a
    la permission *perm* pour l'objet *obj*.

    Par exemple:

    .. code-block:: django

        {% ifhasperm "editer" article %}
            Vous pouvez éditer cet article.
        {% else %}
            Vous ne pouvez pas éditer cet article.
        {% endif %}

{% withperms *obj* as *obj_perms* %}
    Ce *template tag* crée une nouvelle variable *obj_perms* qui se comporte un peu
    comme la variable *perms* de Django, mais qui permet de tester les
    permissions de l'objet en question. C'est utile lorsqu'on veut tester
    plusieurs permissions sur un même objet:

    .. code-block:: django

        {% withperms article as article_perms %}
        {% if article_perms.editer or article_perms.rediger %}
            Vous pouvez agir sur cet article
        {% elif article_perms.voir %}
            Vous pourrez au moins voir cet article
        {% endif %}

Pour que ces *template tags* fonctionnent, le template doit avoir accès à la
requête. Il faut donc ajouter ceci aux settings::

    TEMPLATE_CONTEXT_PROCESSORS = (
        'django.core.context_processors.request',
        ...
    )

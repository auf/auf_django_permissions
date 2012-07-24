Rôles
=====

Dans le cadre d':mod:`auf.django.permissions`, les permissions sont attribuées aux
utilisateurs par des rôles. Un rôle est un objet qui détermine si l'utilisateur
a une permission donnée et sur quels objets cette permission s'applique. Un
utilisateur peut avoir plusieurs rôles et se verra attribuer le cumul des
permissions données par chacun de ses rôles.

Un rôle doit fournir les deux méthodes suivantes:

.. function:: has_perm(self, perm)

   Retourne un booléen qui indique si un utilisateur muni de ce rôle a la
   permission *perm*.

.. function:: get_filter_for_perm(self, perm, model)

   Retourne un filtre qui indique pour quelles instances du modèle Django
   *model* un utilisateur muni de ce rôle a la permission *perm*.  Ce filtre
   peut être un booléen ou un objet Q.

   Si le filtre est ``True``, l'utilisateur a la permission pour toutes les
   instances.

   Si le filtre est ``False``, l'utilisateur n'a la permission pour aucune des
   instances.

   Si le filtre est un objet Q, l'utilisateur a la permission pour les
   instances qui satisfont l'objet Q.

On pourrait, par exemple, définir des rôles d'éditeur pour chaque section d'un
journal de la façon suivante::

    class Editeur(object):

        def __init__(self, section):
            self.section = section

        def has_perm(self, perm):
            if perm == 'lire_le_journal':
                return True
            return False

        def get_filter_for_perm(self, perm, model):
            if model is Article:
                if perm == 'voir':
                    return True
                if perm == 'editer':
                    return Q(section=self.section)
            return False

    editeur_sports = Editeur('sports')
    editeur_voyages = Editeur('voyages')

Ainsi, le rôle ``editeur_sports`` donne à ses utilisateurs la permission globale
``lire_le_journal``, la permission ``voir`` pour tous les articles, et la
permission ``editer`` pour les articles de la section des sports seulement.

Fournisseurs de rôles
---------------------

Une fois que les rôles sont définis, il faut indiquer à
:mod:`auf.django.permissions` quels rôles sont attribués à quels utilisateurs.
Pour ce faire, on définit des fournisseurs de rôles. Un fournisseur de rôles est
simplement une fonction qui prend un utilisateur en paramètre et qui retourne
une liste de rôles. Par exemple::

    def mon_fournisseur(user):
        if user.username == 'alice':
            return [Editeur('sports')]
        elif user.username == 'bob':
            return [Editeur('voyages'), Editeur('affaires')]
        else:
            return []

Ce fournisseur de rôles fait d'Alice l'éditrice des sports et de Bob l'éditeur
des sections voyages et affaires. Pour enregistrer cette fonction comme
fournisseur de rôles, il suffit de l'ajouter aux settings Django comme ceci::

    ROLE_PROVIDERS = (
        'chemin.du.module.mon_fournisseur',
        ...
    )

Un rôle peut être un modèle
---------------------------

Dans bien des cas, on voudra faire des rôles un modèle Django, histoire de
pouvoir associer les rôles aux utilisateurs via l'admin. Reprenons notre exemple
de journal et définissons deux rôles: les journalistes pourront rédiger un
article dans n'importe quelle section, et les éditeurs pourront éditer un
article dans leur section::

    from django.contrib.auth.models import User
    from django.db import models
    from django.db.models import Q


    class JournalRole(models.Model):
        ROLE_CHOICES = (
            (u'journaliste', u'Journaliste'),
            (u'editeur', u'Éditeur'),
        )
        SECTION_CHOICES = (
            (u'sports', u'Sports'),
            (u'affaires', u'Affaires'),
            (u'voyages', u'Voyages'),
        )

        user = models.ForeignKey(User, related_name='roles')
        type = models.CharField(max_length=15, choices=ROLE_CHOICES)
        section = models.CharField(max_length=15, choices=SECTION_CHOICES)

        def has_perm(self, perm):
            return False

        def get_filter_for_model(self, perm, model):
            if self.type == 'journaliste':
                if model is Article and perm == 'rediger':
                    return True

            if self.type == 'editeur':
                if model is Article and perm == 'editer':
                    return Q(section=self.section)

            return False

On pourra, par exemple, permettre l'association de ces rôles aux utilisateurs en
ajoutant un "inline" à l'admin des utilisateurs.

Puisqu'on a mis en place la relation inverse des utilisateurs vers les rôles à
l'aide du paramètre ``related_name`` du champ ``user``, on peut créer facilement
un fournisseur de rôles::

    def fournisseur(user):
        if user.is_anonymous():
            return []
        else:
            return user.roles.all()

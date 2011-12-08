from auf.django.permissions import user_has_perm

class AuthenticationBackend(object):
    supports_anonymous_user = True
    supports_inactive_user = True
    supports_object_permissions = True

    def has_perm(self, user, perm, obj=None):
        return user_has_perm(user, perm, obj)
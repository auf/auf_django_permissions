from django import forms


def make_global_permissions_form(base_form, global_permissions,
                                 prefix='global.'):

    class _GlobalPermissionsForm(forms.ModelForm):

        def __init__(self, *args, **kwargs):
            instance = kwargs.get('instance')
            initial = kwargs.get('initial', {})
            if instance:
                perms = instance.global_permissions.get_permissions()
            else:
                perms = []
            permission_data = {}
            for field, label in global_permissions:
                perm = prefix + field
                permission_data[field] = perm in perms
            permission_data.update(initial)
            kwargs['initial'] = permission_data
            super(_GlobalPermissionsForm, self).__init__(*args, **kwargs)

        def save(self, commit=True):
            instance = super(_GlobalPermissionsForm, self).save(commit=commit)
            old_save_m2m = getattr(self, 'save_m2m')

            def save_m2m():
                if old_save_m2m:
                    old_save_m2m()
                for field, label in global_permissions:
                    perm = prefix + field
                    if self.cleaned_data[field]:
                        instance.global_permissions.add_permission(perm)
                    else:
                        instance.global_permissions.remove_permission(perm)

            if commit:
                save_m2m()
            else:
                self.save_m2m = save_m2m
            return instance

    fields = {}
    for field, label in global_permissions:
        fields[field] = forms.BooleanField(
            label=label, required=False
        )
    form = type('UserOrGroupForm', (_GlobalPermissionsForm, base_form), fields)
    return form

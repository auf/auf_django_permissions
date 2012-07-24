# encoding: utf-8

from django.contrib.admin import ModelAdmin


class GuardedModelAdmin(ModelAdmin):

    def has_change_permission(self, request, obj=None):
        if obj is not None:
            return request.user.has_perm('change', obj)
        else:
            return super(GuardedModelAdmin, self) \
                    .has_change_permission(request, obj)

    def queryset(self, request):
        return super(GuardedModelAdmin, self).queryset(request) \
                .with_perm(request.user, 'change')

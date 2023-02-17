from django.db.models import FileField
from django.utils.translation import gettext_lazy as _


class AdminPermissionsMixin:
    def has_add_permission(self, request):
        return self.model.objects.has_add_permission(request.user)

    def has_change_permission(self, request, obj=None):
        if not obj:
            return True
        return obj.user_has_change_permission(request.user)

    def has_delete_permission(self, request, obj=None):
        if not obj:
            return True
        return obj.user_has_delete_permission(request.user)


class ModelWithFileFieldAdminMixin:
    def get_fieldsets(self, request, obj=None):
        file_fields_names = [f.name for f in self.model._meta.get_fields() if isinstance(f, FileField)]
        fieldsets = []
        for fieldset in super().get_fieldsets(request, obj):
            fieldset[1]['fields'] = [f for f in fieldset[1]['fields'] if f not in file_fields_names]
            fieldsets.append(fieldset)
        if obj:
            fieldsets.append((
                _('Файлы'), {
                    'fields': file_fields_names
                }
            ))
        return fieldsets

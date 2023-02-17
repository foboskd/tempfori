from django.contrib import admin

from main import models as main_models


@admin.register(main_models.EmailNotification)
class EmailNotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'docs_count', 'created_at', 'updated_at']
    readonly_fields = [
        'created_at', 'updated_at', 'docs_count', 'docs',
    ]

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('docs')

from django.contrib import admin
from django.conf import settings
from django.urls import include, path
from django.conf.urls.static import static

urlpatterns = [
    path('admin/webshell/', include('webshell.urls')),
    path('admin/', admin.site.urls),
    path('doc/', include('d11.urls')),
    path('api/', include([
        path('acc/', include('acc.api.urls')),
        path('d11/', include('d11.api.urls')),
        path('', include('project.contrib.drf.schema.urls')),
    ])),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

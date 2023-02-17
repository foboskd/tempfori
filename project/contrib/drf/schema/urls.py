from django.urls import path

from .views import SchemaView

urlpatterns = [
    path('swagger/', SchemaView.with_ui('swagger', cache_timeout=0)),
    path('redoc/', SchemaView.with_ui('redoc', cache_timeout=0)),
]

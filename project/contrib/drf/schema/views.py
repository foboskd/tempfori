from django.conf import settings
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from project.contrib.drf.permissions import IsAuthenticatedOrReadOnly

SchemaViewBase = get_schema_view(
    openapi.Info(
        title=settings.PROJECT_API_TITLE,
        default_version='v1',
    ),
    public=True,
    permission_classes=[IsAuthenticatedOrReadOnly],
)


class SchemaView(SchemaViewBase):
    pass

from rest_framework import routers

from . import views


class Router(routers.DefaultRouter):
    pass


router = Router()
router.register('source', views.SourceViewSet)
router.register('ref', views.RefViewSet)
router.register('doc-field', views.DocFieldViewSet)
router.register('doc', views.DocViewSet)

urlpatterns = []
urlpatterns += router.urls

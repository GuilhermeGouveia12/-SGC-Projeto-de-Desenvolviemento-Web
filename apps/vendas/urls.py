from rest_framework.routers import DefaultRouter
from .views import VendaViewSet

router = DefaultRouter()
router.register(r'', VendaViewSet, basename='vendas')

urlpatterns = router.urls

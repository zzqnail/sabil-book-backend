from django.conf import settings
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter

from sabil_book.users.views import ProviderProfileViewSet
from sabil_book.users.views import UserViewSet

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

router.register("users", UserViewSet)
router.register("providers", ProviderProfileViewSet, basename="provider")


app_name = "api"
urlpatterns = router.urls

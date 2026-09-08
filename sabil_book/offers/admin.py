from django.contrib import admin

from allauth.account.decorators import secure_admin_login
from django.conf import settings
from django.contrib.auth import admin as auth_admin
from django.utils.translation import gettext_lazy as _

from .models import Offer,Order

if settings.DJANGO_ADMIN_FORCE_ALLAUTH:
    # Force the `admin` sign in process to go through the `django-allauth` workflow:
    # https://docs.allauth.org/en/latest/common/admin.html#admin
    admin.autodiscover()
    admin.site.login = secure_admin_login(admin.site.login)  # type: ignore[method-assign]

@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ["request", "provider", "status", "price"]
    list_filter = ["status"]
    search_fields = ["provider", "request"]

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["offer", "status", "funded_at"]
    list_filter = ["status"]
    search_fields = ["offer"]

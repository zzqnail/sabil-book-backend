from allauth.account.decorators import secure_admin_login
from django.conf import settings
from django.contrib import admin

from .models import Dispute
from .models import Review

if settings.DJANGO_ADMIN_FORCE_ALLAUTH:
    # Force the `admin` sign in process to go through the `django-allauth` workflow:
    # https://docs.allauth.org/en/latest/common/admin.html#admin
    admin.autodiscover()
    admin.site.login = secure_admin_login(admin.site.login)  # type: ignore[method-assign]

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ["order", "rating"]
    list_filter = ["rating"]
    search_fields = ["order", "body"]


@admin.register(Dispute)
class DisputeAdmin(admin.ModelAdmin):
    list_display = ["order"]
    list_filter = ["order"]
    search_fields = ["order"]

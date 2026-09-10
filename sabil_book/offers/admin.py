from django.contrib import admin

from .models import Attachment
from .models import Offer
from .models import Order


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ["request", "provider", "status", "price"]
    list_filter = ["status"]
    search_fields = ["provider__user__email", "request__customer__email"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["offer", "status", "funded_at"]
    list_filter = ["status"]


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ["order"]
    list_filter = ["order__status"]
    search_fields = ["file_hash", "storage_key"]

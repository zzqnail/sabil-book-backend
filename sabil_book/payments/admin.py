from django.contrib import admin

from .models import Payment
from .models import Payout


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ["order", "provider", "currency", "status"]
    list_filter = ["status", "currency"]
    search_fields = ["provider"]


@admin.register(Payout)
class PayoutAdmin(admin.ModelAdmin):
    list_display = ["order", "provider", "status"]
    list_filter = ["status"]
    search_fields = ["provider"]

from django.contrib import admin

from .models import Dispute
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ["order", "rating"]
    list_filter = ["rating"]
    search_fields = ["body"]


@admin.register(Dispute)
class DisputeAdmin(admin.ModelAdmin):
    list_display = ["order"]
    list_filter = ["order__status"]

from django.db import models

# Create your models here.
from django.db.models import CharField
from django.db.models import DecimalField
from django.utils.translation import gettext_lazy as _

from sabil_book.offers.models import Order


class Review(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="review",
        verbose_name=_("order"),
    )
    rating = DecimalField(
        _("Review Rating"),
        max_digits=2,
        decimal_places=1,
        default=0,
    )
    body = CharField(
        _("Review Body"),
        max_length=255,
        blank=True,
    )

    def __str__(self) -> str:
        return f"Review of {self.order} ({self.rating})"


class Dispute(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="dispute",
        verbose_name=_("order"),
    )
    reason = CharField(
        _("Dipute reason"),
        max_length=255,
        default="",
    )
    resolution = CharField(
        _("Dispute resolution"),
        max_length=255,
        default="",
    )

    def __str__(self) -> str:
        return f"Dispute on {self.order} ({self.reason})"

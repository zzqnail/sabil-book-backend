from django.db import models

# Create your models here.
from django.db import models

from django.db.models import CharField, DecimalField
from django.utils.translation import gettext_lazy as _

from sabil_book.offers.models import Order

class Payment(models.Model):
    class PaymentCurrency(models.TextChoices):
        QAR = "qat. riyal", _("Qat. Riyal")
        USD = "US. dollar", _("US Dollar")
        KZT = "tenge", _("Tenge")

    class PaymentStatus(models.TextChoices):
        PENDING = "pending", _("Pending")
        PROCESSING = "processing", _("Processing")   # sent to payment provider, awaiting confirmation
        SUCCEEDED = "succeeded", _("Succeeded")
        FAILED = "failed", _("Failed")
        REFUNDED = "refunded", _("Refunded")
        CANCELLED = "cancelled", _("Cancelled")

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="payment",
        verbose_name=_("order"),
    )
    provider = CharField(
        _("Payment Provider"),
        max_length=255,
        blank=False,
        default="",
    )
    currency = CharField(
        _("Payment Currency"),
        max_length=25,
        choices=PaymentCurrency.choices,
        default=PaymentCurrency.QAR,
    )

    status = CharField(
        _("Payment Status"),
        max_length=25,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
    )

    def __str__(self) -> str:
        return f"Payment for {self.order} ({self.get_status_display()})"

class Payout(models.Model):
    class PayoutStatus(models.TextChoices):
        PENDING = "pending", _("Pending")
        ON_HOLD = "on_hold", _("On Hold")            # e.g. provider's KYC isn't APPROVED yet
        PROCESSING = "processing", _("Processing")
        PAID = "paid", _("Paid")
        FAILED = "failed", _("Failed")
        CANCELLED = "cancelled", _("Cancelled")

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="payout",
        verbose_name=_("order"),
    )
    provider = CharField(
        _("Payout Provider"),
        max_length=255,
        blank=False,
        default=""
    )
    status = CharField(
        _("Payout Status"),
        max_length=25,
        choices=PayoutStatus.choices,
        default=PayoutStatus.PENDING,
    )

    def __str__(self) -> str:
        return f"Payout for {self.order} ({self.get_status_display()})"

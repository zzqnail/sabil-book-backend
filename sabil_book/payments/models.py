from django.db import models

# Create your models here.
from django.db.models import CharField
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from sabil_book.offers.models import Order


class Payment(models.Model):
    class PaymentCurrency(models.TextChoices):
        QAR = "QAR", _("Qatari Riyal")
        USD = "USD", _("US Dollar")
        KZT = "KZT", _("Tenge")

    class PaymentStatus(models.TextChoices):
        PENDING = "pending", _("Pending")
        PROCESSING = "processing", _("Processing")  # sent to provider, awaiting result
        SUCCEEDED = "succeeded", _("Succeeded")
        FAILED = "failed", _("Failed")
        REFUNDED = "refunded", _("Refunded")
        CANCELLED = "cancelled", _("Cancelled")

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name=_("order"),
    )
    amount = models.DecimalField(
        _("Payment Amount"),
        max_digits=10,
        decimal_places=2,
    )
    provider = CharField(
        _("Payment Provider"),
        max_length=255,
        blank=False,
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

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=~Q(provider=""),
                name="payment_provider_not_blank",
            ),
        ]

    def __str__(self) -> str:
        return f"Payment for {self.order} ({self.get_status_display()})"


class Payout(models.Model):
    class PayoutStatus(models.TextChoices):
        PENDING = "pending", _("Pending")
        ON_HOLD = "on_hold", _("On Hold")  # e.g. provider's KYC isn't APPROVED
        PROCESSING = "processing", _("Processing")
        PAID = "paid", _("Paid")
        FAILED = "failed", _("Failed")
        CANCELLED = "cancelled", _("Cancelled")

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="payouts",
        verbose_name=_("order"),
    )
    amount = models.DecimalField(
        _("Payout Amount"),
        max_digits=10,
        decimal_places=2,
    )
    currency = CharField(
        _("Payout Currency"),
        max_length=25,
        choices=Payment.PaymentCurrency.choices,
        default=Payment.PaymentCurrency.QAR,
    )
    provider = CharField(
        _("Payout Provider"),
        max_length=255,
        blank=False,
    )
    status = CharField(
        _("Payout Status"),
        max_length=25,
        choices=PayoutStatus.choices,
        default=PayoutStatus.PENDING,
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=~Q(provider=""),
                name="payout_provider_not_blank",
            ),
        ]

    def __str__(self) -> str:
        return f"Payout for {self.order} ({self.get_status_display()})"

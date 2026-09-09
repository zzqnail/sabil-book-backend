from django.db import models

# Create your models here.
from django.conf import settings
from django.db import models
from sabil_book.users.models import ProviderProfile, Request
from django.db.models import CharField, DateTimeField
from django.utils.translation import gettext_lazy as _

class Offer(models.Model):
    class OfferStatus(models.TextChoices):
        PENDING = "pending", _("Pending")      # submitted, awaiting customer decision
        ACCEPTED = "accepted", _("Accepted")   # customer picked this one
        REJECTED = "rejected", _("Rejected")   # customer declined it
        WITHDRAWN = "withdrawn", _("Withdrawn")  # provider pulled it back
        EXPIRED = "expired", _("Expired")   # after validity window
    
    request = models.ForeignKey(
        Request,
        on_delete=models.CASCADE,
        related_name="offer",
        verbose_name=_("request"),
    )
    provider = models.ForeignKey(
        ProviderProfile,
        on_delete=models.CASCADE,
        related_name="offer",
        verbose_name=_("provider"),
    )
    price = CharField(
        _("Offering Price"),
        max_length=20,
        default=0,
    )
    status = CharField(
        _("Offer status"),
        max_length=25,
        choices=OfferStatus.choices,
        default=OfferStatus.PENDING,
    )

    def __str__(self) -> str:
        return f"{self.provider} on {self.request} ({self.get_status_display()})"

class Message(models.Model):
    offer = models.ForeignKey(
        Offer,
        on_delete=models.CASCADE,
        related_name="message",
        verbose_name=_("offer"),
    )

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user",
        verbose_name=_("sender"),
    )
    body = models.CharField(
        _("Message Body"),
        max_length=255,
    )
    date_time = DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.sender}: {self.body[:30]}"

class Order(models.Model):
    class OrderStatus(models.TextChoices):
        FUNDED = "funded", _("Funded")
        SENT = "sent", _("Sent")
        CONFIRMED = "confirmed", _("Confirmed")
        APPEAL = "appeal", _("Appeal")
        DISPUTE = "dispute", _("Dispute")
        UNRESOLVED = "unresolved", _("Unresolved")
        REVERTED = "reverted", _("Reverted")


    offer = models.ForeignKey(
        Offer,
        on_delete=models.CASCADE,
        related_name="order",
        verbose_name=_("offer"),
    )
    status = models.CharField(
        _("status"),
        max_length=25,
        choices=OrderStatus.choices,
        default=OrderStatus.FUNDED,
    )
    funded_at = DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Order for {self.offer} ({self.get_status_display()})"

class Attachment(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="attachment",
        verbose_name=_("order"),
    )
    file_hash = CharField(
        _("Attached file hash"),
        max_length=255,
        blank=True,
    )
    storage_key=CharField(
        _("Attached file key"),
        max_length=255,
        blank=True,
    )

    def __str__(self):
        return f"Attached file for {self.order} - {self.storage_key}"
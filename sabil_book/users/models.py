import uuid
from typing import ClassVar

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import CharField
from django.db.models import EmailField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from .managers import UserManager


class User(AbstractUser):
    """
    Default custom user model for sabil_book.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    # First and last name do not cover name patterns around the globe
    uuid = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        db_index=True,
    )
    name = CharField(_("Name of User"), blank=True, max_length=255)
    first_name = None  # type: ignore[assignment]
    last_name = None  # type: ignore[assignment]
    email = EmailField(_("email address"), unique=True)
    username = None  # type: ignore[assignment]
    country = CharField(_("User location"), blank=True, max_length=255)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects: ClassVar[UserManager] = UserManager()

    def get_absolute_url(self) -> str:
        """Get URL for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"pk": self.id})

class ProviderProfile(models.Model):
    class KYCStatus(models.TextChoices):
        NOT_SUBMITTED = "not_submitted", _("Not Submitted")
        PENDING = "pending", _("Pending Review")
        APPROVED = "approved", _("Approved")
        REJECTED = "rejected", _("Rejected")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="provider_profile",
        verbose_name=_("user"),
    )
    kyc_status = models.CharField(
        _("KYC status"),
        max_length=20,
        choices=KYCStatus.choices,
        default=KYCStatus.NOT_SUBMITTED,
    )
    payout_provider = models.CharField(
        _("Payout provider"),
        max_length=225,
        blank=True,
    )

    def __str__(self) -> str:
        return f"{self.user} ({self.get_kyc_status_display()})"

class Request(models.Model):
    class RequestCategory(models.TextChoices):
        DOCUMENT = "document", _("Document")
        COURSE = "course", _("Course")
        BOOK = "book", _("Book")
        JOURNAL = "journal", _("Journal")
        ARTICLE = "article", _("Article")
        OTHER = "other", _("Other")

    class RequestStatus(models.TextChoices):
        DRAFT = "draft", _("Draft")           # customer is still filling it in
        OPEN = "open", _("Open")              # published, visible to providers
        IN_PROGRESS = "in_progress", _("In Progress")  # a provider accepted it
        FULFILLED = "fulfilled", _("Fulfilled")        # provider delivered it
        CANCELLED = "cancelled", _("Cancelled")        # customer withdrew it
        EXPIRED = "expired", _("Expired")              # no provider took it in time

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="request_customer",
        verbose_name=_("user"),
    )
    category = models.CharField(
        _("Request Category"),
        max_length=25,
        choices=RequestCategory.choices,
        default=RequestCategory.OTHER,
    )
    budget = models.CharField(
        _("Request Budget"),
        max_length=255,
        blank=True,
        default="",
    )
    status = models.CharField(
        _("Request Status"),
        max_length=25,
        choices=RequestStatus.choices,
        blank=False,
        default=RequestStatus.DRAFT,
    )

    def __str__(self) -> str:
        return f"{self.customer} - {self.get_category_display()}"

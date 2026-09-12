from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Request(models.Model):
    class RequestCategory(models.TextChoices):
        RESEARCH_BRIEF = "research_brief", _("Research brief")
        PROFESSIONAL_TEMPLATE = "professional_template", _(
            "Professional template / SOP",
        )
        CERTIFICATION_MATERIAL = "certification_material", _(
            "Certification material",
        )

    class RequestStatus(models.TextChoices):
        DRAFT = "draft", _("Draft")
        MANUAL_REVIEW = "manual_review", _("Manual review")
        PUBLISHED = "published", _("Published")
        REJECTED = "rejected", _("Rejected")
        CLOSED = "closed", _("Closed")

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="material_requests",
        verbose_name=_("user"),
    )
    category = models.CharField(
        _("Request Category"),
        max_length=32,
        choices=RequestCategory.choices,
    )
    title = models.CharField(_("title"), max_length=255)
    description = models.TextField(_("description"))
    budget = models.DecimalField(
        _("Request Budget"),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )
    status = models.CharField(
        _("Request Status"),
        max_length=32,
        choices=RequestStatus.choices,
        default=RequestStatus.DRAFT,
    )
    moderation_flags = models.JSONField(_("moderation flags"), default=list, blank=True)
    rejection_reason = models.TextField(_("rejection reason"), blank=True)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)
    published_at = models.DateTimeField(_("published at"), null=True, blank=True)
    closed_at = models.DateTimeField(_("closed at"), null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.customer} - {self.get_category_display()}"

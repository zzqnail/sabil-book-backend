from dataclasses import dataclass

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from .models import Request


class InvalidTransitionError(ValueError):
    """Raised when a request cannot move to the desired state."""


@dataclass(frozen=True)
class ModerationResult:
    matched_terms: list[str]

    @property
    def requires_manual_review(self) -> bool:
        return bool(self.matched_terms)


def check_content(request: Request) -> ModerationResult:
    content = f"{request.title}\n{request.description}".casefold()
    blocklist = getattr(settings, "REQUEST_MODERATION_BLOCKLIST", [])
    normalized_terms = {
        term.strip().casefold()
        for term in blocklist
        if isinstance(term, str) and term.strip()
    }
    matches = sorted(term for term in normalized_terms if term in content)
    return ModerationResult(matched_terms=matches)


@transaction.atomic
def submit_request(request_id: int) -> Request:
    request = Request.objects.select_for_update().get(pk=request_id)
    if request.status not in {
        Request.RequestStatus.DRAFT,
        Request.RequestStatus.REJECTED,
    }:
        msg = "Only a draft or rejected request can be submitted."
        raise InvalidTransitionError(msg)

    request.rejection_reason = ""
    result = check_content(request)
    request.moderation_flags = result.matched_terms
    if result.requires_manual_review:
        request.status = Request.RequestStatus.MANUAL_REVIEW
        request.published_at = None
    else:
        request.status = Request.RequestStatus.PUBLISHED
        request.published_at = timezone.now()
    request.save(
        update_fields=[
            "status",
            "rejection_reason",
            "moderation_flags",
            "published_at",
            "updated_at",
        ],
    )
    return request


@transaction.atomic
def moderate_request(request_id: int, *, approve: bool, reason: str = "") -> Request:
    request = Request.objects.select_for_update().get(pk=request_id)
    if request.status != Request.RequestStatus.MANUAL_REVIEW:
        msg = "Only requests awaiting manual review can be moderated."
        raise InvalidTransitionError(msg)
    if not approve and not reason.strip():
        msg = "A rejection reason is required."
        raise InvalidTransitionError(msg)

    request.status = (
        Request.RequestStatus.PUBLISHED
        if approve
        else Request.RequestStatus.REJECTED
    )
    request.rejection_reason = "" if approve else reason.strip()
    request.published_at = timezone.now() if approve else None
    request.save(
        update_fields=["status", "rejection_reason", "published_at", "updated_at"],
    )
    return request


@transaction.atomic
def close_request(request_id: int) -> Request:
    request = Request.objects.select_for_update().get(pk=request_id)
    if request.status != Request.RequestStatus.PUBLISHED:
        msg = "Only a published request can be closed."
        raise InvalidTransitionError(msg)
    request.status = Request.RequestStatus.CLOSED
    request.closed_at = timezone.now()
    request.save(update_fields=["status", "closed_at", "updated_at"])
    return request

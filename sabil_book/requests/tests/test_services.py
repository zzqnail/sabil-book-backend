import pytest

from sabil_book.requests.services import check_content
from sabil_book.requests.tests.factories import RequestFactory


@pytest.mark.django_db
def test_content_check_ignores_blank_and_non_string_terms(settings):
    settings.REQUEST_MODERATION_BLOCKLIST = ["", "   ", None, "FORBIDDEN"]
    request = RequestFactory(
        title="Allowed title",
        description="Contains a forbidden term.",
    )

    result = check_content(request)

    assert result.matched_terms == ["forbidden"]
    assert result.requires_manual_review


@pytest.mark.django_db
def test_content_check_allows_content_when_blocklist_is_empty(settings):
    settings.REQUEST_MODERATION_BLOCKLIST = []
    request = RequestFactory()

    result = check_content(request)

    assert result.matched_terms == []
    assert not result.requires_manual_review

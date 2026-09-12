import pytest
from django.core.exceptions import ValidationError

from sabil_book.requests.models import Request
from sabil_book.requests.tests.factories import RequestFactory


class TestRequest:
    def test_category_is_required(self, user):
        request = Request(
            customer=user,
            title="Research request",
            description="Research description",
        )
        with pytest.raises(ValidationError) as exc_info:
            request.full_clean()
        assert "category" in exc_info.value.error_dict

    def test_budget_is_optional(self, user):
        request = Request.objects.create(
            customer=user,
            category=Request.RequestCategory.RESEARCH_BRIEF,
            title="Research request",
            description="Research description",
        )
        assert request.budget is None

    def test_str_includes_customer_and_category(self, db):
        request = RequestFactory.create(
            category=Request.RequestCategory.RESEARCH_BRIEF,
        )
        assert str(request) == f"{request.customer} - Research brief"

    def test_deleted_when_customer_is_deleted(self, user):
        request = RequestFactory.create(customer=user)
        user.delete()
        assert not Request.objects.filter(pk=request.pk).exists()


@pytest.mark.django_db
def test_request_factory_creates_valid_instance():
    request = RequestFactory.create()
    assert request.pk is not None
    assert request.customer_id is not None

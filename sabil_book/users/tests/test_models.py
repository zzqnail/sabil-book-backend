from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from sabil_book.users.models import ProviderProfile
from sabil_book.users.models import Request
from sabil_book.users.tests.factories import ProviderProfileFactory
from sabil_book.users.tests.factories import RequestFactory
from sabil_book.users.tests.factories import UserFactory

if TYPE_CHECKING:
    from sabil_book.users.models import User


def test_user_get_absolute_url(user: User):
    assert user.get_absolute_url() == f"/users/{user.pk}/"


def test_user_str_returns_email(user: User):
    assert str(user) == user.email


def test_user_uuid_is_unique_per_instance(db):
    first_user = UserFactory.create()
    second_user = UserFactory.create()
    assert first_user.uuid != second_user.uuid


class TestProviderProfile:
    def test_defaults_to_not_submitted_kyc_status(self, user: User):
        profile = ProviderProfile.objects.create(user=user)
        assert profile.kyc_status == ProviderProfile.KYCStatus.NOT_SUBMITTED

    def test_str_includes_user_and_kyc_status(self, db):
        profile = ProviderProfileFactory.create(
            kyc_status=ProviderProfile.KYCStatus.APPROVED,
        )
        assert str(profile) == f"{profile.user} (Approved)"

    def test_deleted_when_user_is_deleted(self, user: User):
        profile = ProviderProfileFactory.create(user=user)
        user.delete()
        assert not ProviderProfile.objects.filter(pk=profile.pk).exists()


class TestRequest:
    def test_defaults_to_other_category(self, user: User):
        request = Request.objects.create(customer=user)
        assert request.category == Request.RequestCategory.OTHER

    def test_budget_is_optional(self, user: User):
        request = Request.objects.create(customer=user)
        assert request.budget is None

    def test_str_includes_customer_and_category(self, db):
        request = RequestFactory.create(category=Request.RequestCategory.BOOK)
        assert str(request) == f"{request.customer} - Book"

    def test_deleted_when_customer_is_deleted(self, user: User):
        request = RequestFactory.create(customer=user)
        user.delete()
        assert not Request.objects.filter(pk=request.pk).exists()


@pytest.mark.django_db
def test_provider_profile_factory_creates_valid_instance():
    profile = ProviderProfileFactory.create()
    assert profile.pk is not None
    assert profile.user_id is not None


@pytest.mark.django_db
def test_request_factory_creates_valid_instance():
    request = RequestFactory.create()
    assert request.pk is not None
    assert request.customer_id is not None

from __future__ import annotations

from http import HTTPStatus

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from sabil_book.offers.tests.factories import MessageFactory
from sabil_book.offers.tests.factories import OfferFactory
from sabil_book.requests.tests.factories import RequestFactory
from sabil_book.users.tests.factories import ProviderProfileFactory
from sabil_book.users.tests.factories import UserFactory


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.mark.django_db
def test_customer_can_list_message_history_in_order(api_client):
    customer = UserFactory.create()
    provider_profile = ProviderProfileFactory.create()
    offer = OfferFactory.create(
        request=RequestFactory.create(customer=customer),
        provider=provider_profile,
    )
    older = MessageFactory.create(offer=offer, sender=customer, body="first")
    newer = MessageFactory.create(
        offer=offer,
        sender=provider_profile.user,
        body="second",
    )

    api_client.force_authenticate(customer)
    response = api_client.get(reverse("api:offer-messages", args=[offer.id]))

    assert response.status_code == HTTPStatus.OK
    assert [item["id"] for item in response.data["results"]] == [older.id, newer.id]


@pytest.mark.django_db
def test_provider_can_also_list_message_history(api_client):
    provider_profile = ProviderProfileFactory.create()
    offer = OfferFactory.create(provider=provider_profile)
    MessageFactory.create(offer=offer)

    api_client.force_authenticate(provider_profile.user)
    response = api_client.get(reverse("api:offer-messages", args=[offer.id]))

    assert response.status_code == HTTPStatus.OK
    assert len(response.data["results"]) == 1


@pytest.mark.django_db
def test_stranger_gets_not_found_instead_of_forbidden(api_client):
    offer = OfferFactory.create()
    MessageFactory.create(offer=offer)

    api_client.force_authenticate(UserFactory.create())
    response = api_client.get(reverse("api:offer-messages", args=[offer.id]))

    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.django_db
def test_anonymous_user_cannot_list_message_history(api_client):
    offer = OfferFactory.create()

    response = api_client.get(reverse("api:offer-messages", args=[offer.id]))

    assert response.status_code == HTTPStatus.FORBIDDEN

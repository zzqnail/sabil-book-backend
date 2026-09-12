from http import HTTPStatus

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from sabil_book.requests.models import Request
from sabil_book.users.tests.factories import UserFactory


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def request_payload() -> dict:
    return {
        "category": Request.RequestCategory.RESEARCH_BRIEF,
        "title": "Market research brief",
        "description": "Research the market and summarize its key trends.",
        "budget": "250.00",
    }


@pytest.mark.django_db
def test_clean_request_completes_draft_to_publish_flow(api_client, request_payload):
    user = UserFactory()
    api_client.force_authenticate(user)

    create_response = api_client.post(reverse("api:request-list"), request_payload)
    assert create_response.status_code == HTTPStatus.CREATED
    assert create_response.data["status"] == Request.RequestStatus.DRAFT

    submit_response = api_client.post(
        reverse("api:request-submit", args=[create_response.data["id"]]),
    )
    assert submit_response.status_code == HTTPStatus.OK
    assert submit_response.data["status"] == Request.RequestStatus.PUBLISHED

    browse_response = api_client.get(reverse("api:browse-list"))
    assert browse_response.status_code == HTTPStatus.OK
    assert [item["id"] for item in browse_response.data] == [
        create_response.data["id"],
    ]


@pytest.mark.django_db
def test_suspicious_request_waits_for_manual_approval(
    api_client,
    request_payload,
    settings,
):
    settings.REQUEST_MODERATION_BLOCKLIST = ["forbidden phrase"]
    customer = UserFactory()
    api_client.force_authenticate(customer)
    request_payload["description"] = "Contains a forbidden phrase."
    create_response = api_client.post(reverse("api:request-list"), request_payload)

    submit_response = api_client.post(
        reverse("api:request-submit", args=[create_response.data["id"]]),
    )
    assert submit_response.data["status"] == Request.RequestStatus.MANUAL_REVIEW
    assert submit_response.data["moderation_flags"] == ["forbidden phrase"]
    browse_ids = [
        item["id"] for item in api_client.get(reverse("api:browse-list")).data
    ]
    assert create_response.data["id"] not in browse_ids

    admin = UserFactory(is_staff=True)
    api_client.force_authenticate(admin)
    queue_response = api_client.get(reverse("api:request-moderation-list"))
    assert [item["id"] for item in queue_response.data] == [create_response.data["id"]]

    approve_response = api_client.post(
        reverse("api:request-moderation-approve", args=[create_response.data["id"]]),
    )
    assert approve_response.data["status"] == Request.RequestStatus.PUBLISHED
    browse_ids = [
        item["id"] for item in api_client.get(reverse("api:browse-list")).data
    ]
    assert create_response.data["id"] in browse_ids


@pytest.mark.django_db
def test_admin_rejection_requires_and_records_reason(
    api_client,
    request_payload,
    settings,
):
    settings.REQUEST_MODERATION_BLOCKLIST = ["blocked"]
    customer = UserFactory()
    material_request = Request.objects.create(
        customer=customer,
        status=Request.RequestStatus.MANUAL_REVIEW,
        moderation_flags=["blocked"],
        **request_payload,
    )
    admin = UserFactory(is_staff=True)
    api_client.force_authenticate(admin)
    url = reverse("api:request-moderation-reject", args=[material_request.pk])

    assert api_client.post(url, {}).status_code == HTTPStatus.BAD_REQUEST
    response = api_client.post(url, {"reason": "Outside marketplace policy."})
    assert response.status_code == HTTPStatus.OK
    assert response.data["status"] == Request.RequestStatus.REJECTED
    assert response.data["rejection_reason"] == "Outside marketplace policy."


@pytest.mark.django_db
def test_browse_filters_category_and_status(api_client, request_payload):
    customer = UserFactory()
    matching = Request.objects.create(
        customer=customer,
        status=Request.RequestStatus.PUBLISHED,
        **request_payload,
    )
    Request.objects.create(
        customer=customer,
        category=Request.RequestCategory.CERTIFICATION_MATERIAL,
        title="Certification guide",
        description="A guide",
        status=Request.RequestStatus.PUBLISHED,
    )
    Request.objects.create(customer=customer, **request_payload)
    api_client.force_authenticate(UserFactory())

    response = api_client.get(
        reverse("api:browse-list"),
        {
            "category": Request.RequestCategory.RESEARCH_BRIEF,
            "status": Request.RequestStatus.PUBLISHED,
        },
    )
    assert [item["id"] for item in response.data] == [matching.pk]


@pytest.mark.django_db
def test_customer_cannot_access_another_customers_request(api_client):
    request = Request.objects.create(
        customer=UserFactory(),
        category=Request.RequestCategory.RESEARCH_BRIEF,
        title="Private draft",
        description="Only its customer should see this.",
    )
    api_client.force_authenticate(UserFactory())

    response = api_client.get(reverse("api:request-detail", args=[request.pk]))

    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.django_db
def test_published_request_cannot_be_edited(api_client, request_payload):
    customer = UserFactory()
    request = Request.objects.create(
        customer=customer,
        status=Request.RequestStatus.PUBLISHED,
        **request_payload,
    )
    api_client.force_authenticate(customer)

    response = api_client.patch(
        reverse("api:request-detail", args=[request.pk]),
        {"title": "Changed title"},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST

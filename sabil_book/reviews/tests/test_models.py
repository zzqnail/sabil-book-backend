from __future__ import annotations

from decimal import Decimal

import pytest
from django.db import IntegrityError
from django.db import transaction

from sabil_book.offers.tests.factories import OrderFactory
from sabil_book.reviews.models import Dispute
from sabil_book.reviews.models import Review
from sabil_book.reviews.tests.factories import DisputeFactory
from sabil_book.reviews.tests.factories import ReviewFactory
from sabil_book.users.tests.factories import UserFactory


class TestReview:
    def test_str_includes_order_and_rating(self, db):
        review = ReviewFactory.create(rating=Decimal("4.5"))
        assert str(review) == f"Review of {review.order} (4.5)"

    def test_body_is_optional(self, db):
        order = OrderFactory.create()
        author = UserFactory.create()
        review = Review.objects.create(
            order=order,
            author=author,
            rating=Decimal("3.0"),
        )
        assert review.body == ""

    def test_rating_is_required(self, db):
        order = OrderFactory.create()
        author = UserFactory.create()
        with pytest.raises(IntegrityError), transaction.atomic():
            Review.objects.create(order=order, author=author)

    def test_rating_below_one_is_rejected(self, db):
        order = OrderFactory.create()
        author = UserFactory.create()
        with pytest.raises(IntegrityError), transaction.atomic():
            Review.objects.create(order=order, author=author, rating=Decimal("0.5"))

    def test_rating_above_five_is_rejected(self, db):
        order = OrderFactory.create()
        author = UserFactory.create()
        with pytest.raises(IntegrityError), transaction.atomic():
            Review.objects.create(order=order, author=author, rating=Decimal("5.5"))

    def test_author_is_required(self, db):
        order = OrderFactory.create()
        with pytest.raises(IntegrityError), transaction.atomic():
            Review.objects.create(order=order, rating=Decimal("3.0"))

    def test_author_cannot_review_the_same_order_twice(self, db):
        order = OrderFactory.create()
        author = UserFactory.create()
        Review.objects.create(order=order, author=author, rating=Decimal("3.0"))
        with pytest.raises(IntegrityError), transaction.atomic():
            Review.objects.create(order=order, author=author, rating=Decimal("4.0"))

    def test_rating_stores_one_decimal_place(self, db):
        review = ReviewFactory.create(rating=Decimal("4.5"))
        review.refresh_from_db()
        assert review.rating == Decimal("4.5")

    def test_deleted_when_order_is_deleted(self, db):
        review = ReviewFactory.create()
        review.order.delete()
        assert not Review.objects.filter(pk=review.pk).exists()

    def test_order_can_have_multiple_reviews(self, db):
        review_count = 2
        order = OrderFactory.create()
        ReviewFactory.create_batch(review_count, order=order)
        assert order.reviews.count() == review_count


class TestDispute:
    def test_str_includes_order_and_reason(self, db):
        dispute = DisputeFactory.create(reason="item not delivered")
        assert str(dispute) == f"Dispute on {dispute.order} (item not delivered)"

    def test_resolution_defaults_to_empty_string(self, db):
        order = OrderFactory.create()
        dispute = Dispute.objects.create(order=order, reason="item not delivered")
        assert dispute.resolution == ""

    def test_reason_defaults_to_empty_string(self, db):
        order = OrderFactory.create()
        dispute = Dispute.objects.create(order=order)
        assert dispute.reason == ""

    def test_deleted_when_order_is_deleted(self, db):
        dispute = DisputeFactory.create()
        dispute.order.delete()
        assert not Dispute.objects.filter(pk=dispute.pk).exists()

    def test_order_can_only_have_one_dispute(self, db):
        order = OrderFactory.create()
        DisputeFactory.create(order=order)
        with pytest.raises(IntegrityError), transaction.atomic():
            DisputeFactory.create(order=order)


@pytest.mark.django_db
def test_review_factory_creates_valid_instance():
    review = ReviewFactory.create()
    assert review.pk is not None
    assert review.order_id is not None


@pytest.mark.django_db
def test_dispute_factory_creates_valid_instance():
    dispute = DisputeFactory.create()
    assert dispute.pk is not None
    assert dispute.order_id is not None

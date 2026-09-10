from __future__ import annotations

import factory
from factory import Faker
from factory import fuzzy
from factory.django import DjangoModelFactory

from sabil_book.offers.tests.factories import OrderFactory
from sabil_book.reviews.models import Dispute
from sabil_book.reviews.models import Review
from sabil_book.users.tests.factories import UserFactory


class ReviewFactory(DjangoModelFactory[Review]):
    order = factory.SubFactory(OrderFactory)
    author = factory.SubFactory(UserFactory)
    rating = fuzzy.FuzzyDecimal(1.0, 5.0, precision=1)
    body = Faker("sentence")

    class Meta:
        model = Review


class DisputeFactory(DjangoModelFactory[Dispute]):
    order = factory.SubFactory(OrderFactory)
    reason = Faker("sentence")
    resolution = Faker("sentence")

    class Meta:
        model = Dispute

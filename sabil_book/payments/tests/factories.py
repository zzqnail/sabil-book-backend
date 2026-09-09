from __future__ import annotations

import factory
from factory import Faker
from factory import fuzzy
from factory.django import DjangoModelFactory

from sabil_book.offers.tests.factories import OrderFactory
from sabil_book.payments.models import Payment
from sabil_book.payments.models import Payout


class PaymentFactory(DjangoModelFactory[Payment]):
    order = factory.SubFactory(OrderFactory)
    provider = Faker("company")
    currency = fuzzy.FuzzyChoice(Payment.PaymentCurrency.values)
    status = fuzzy.FuzzyChoice(Payment.PaymentStatus.values)

    class Meta:
        model = Payment


class PayoutFactory(DjangoModelFactory[Payout]):
    order = factory.SubFactory(OrderFactory)
    provider = Faker("company")
    status = fuzzy.FuzzyChoice(Payout.PayoutStatus.values)

    class Meta:
        model = Payout

from __future__ import annotations

from decimal import Decimal

import pytest
from django.db import IntegrityError
from django.db import transaction

from sabil_book.offers.tests.factories import OrderFactory
from sabil_book.payments.models import Payment
from sabil_book.payments.models import Payout
from sabil_book.payments.tests.factories import PaymentFactory
from sabil_book.payments.tests.factories import PayoutFactory


class TestPayment:
    def test_defaults(self, db):
        order = OrderFactory.create()
        payment = Payment.objects.create(
            order=order,
            amount=Decimal("100.00"),
            provider="Stripe",
        )
        assert payment.currency == Payment.PaymentCurrency.QAR
        assert payment.status == Payment.PaymentStatus.PENDING

    def test_amount_is_required(self, db):
        order = OrderFactory.create()
        with pytest.raises(IntegrityError), transaction.atomic():
            Payment.objects.create(order=order, provider="Stripe")

    def test_provider_cannot_be_blank(self, db):
        order = OrderFactory.create()
        with pytest.raises(IntegrityError), transaction.atomic():
            Payment.objects.create(order=order, amount=Decimal("100.00"), provider="")

    def test_str_includes_order_and_status(self, db):
        payment = PaymentFactory.create(status=Payment.PaymentStatus.SUCCEEDED)
        assert str(payment) == f"Payment for {payment.order} (Succeeded)"

    def test_deleted_when_order_is_deleted(self, db):
        payment = PaymentFactory.create()
        payment.order.delete()
        assert not Payment.objects.filter(pk=payment.pk).exists()

    def test_order_can_have_multiple_payments(self, db):
        payment_count = 2
        order = OrderFactory.create()
        PaymentFactory.create_batch(payment_count, order=order)
        assert order.payments.count() == payment_count


class TestPayout:
    def test_defaults(self, db):
        order = OrderFactory.create()
        payout = Payout.objects.create(
            order=order,
            amount=Decimal("100.00"),
            provider="Stripe",
        )
        assert payout.currency == Payment.PaymentCurrency.QAR
        assert payout.status == Payout.PayoutStatus.PENDING

    def test_amount_is_required(self, db):
        order = OrderFactory.create()
        with pytest.raises(IntegrityError), transaction.atomic():
            Payout.objects.create(order=order, provider="Stripe")

    def test_provider_cannot_be_blank(self, db):
        order = OrderFactory.create()
        with pytest.raises(IntegrityError), transaction.atomic():
            Payout.objects.create(order=order, amount=Decimal("100.00"), provider="")

    def test_str_includes_order_and_status(self, db):
        payout = PayoutFactory.create(status=Payout.PayoutStatus.ON_HOLD)
        assert str(payout) == f"Payout for {payout.order} (On Hold)"

    def test_deleted_when_order_is_deleted(self, db):
        payout = PayoutFactory.create()
        payout.order.delete()
        assert not Payout.objects.filter(pk=payout.pk).exists()

    def test_order_can_have_multiple_payouts(self, db):
        payout_count = 2
        order = OrderFactory.create()
        PayoutFactory.create_batch(payout_count, order=order)
        assert order.payouts.count() == payout_count


@pytest.mark.django_db
def test_payment_factory_creates_valid_instance():
    payment = PaymentFactory.create()
    assert payment.pk is not None
    assert payment.order_id is not None


@pytest.mark.django_db
def test_payout_factory_creates_valid_instance():
    payout = PayoutFactory.create()
    assert payout.pk is not None
    assert payout.order_id is not None

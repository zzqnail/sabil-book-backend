from __future__ import annotations

import itertools
import random

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from django.db import transaction

from sabil_book.offers.models import Offer
from sabil_book.offers.models import Order

DISPUTE_SAMPLE_RATE = 3
DISPUTED_ORDER_STATUSES = (
    Order.OrderStatus.DISPUTE,
    Order.OrderStatus.UNRESOLVED,
    Order.OrderStatus.REVERTED,
)


def _validate_counts(n_customers, n_providers, n_requests, n_offers, n_messages):
    if n_requests > 0 and n_customers + n_providers == 0:
        msg = "Need at least one customer or provider to create requests."
        raise CommandError(msg)
    if n_offers > 0 and n_requests == 0:
        msg = "Need at least one request to create offers."
        raise CommandError(msg)
    if n_messages > 0 and n_offers == 0:
        msg = "Need at least one offer to create messages."
        raise CommandError(msg)


def _seed_post_order_data(
    orders,
    review_factory,
    payment_factory,
    dispute_factory,
    payout_factory,
):
    confirmed_orders = [
        order for order in orders if order.status == Order.OrderStatus.CONFIRMED
    ]
    for order in orders:
        payment_factory.create(order=order)
    for order in confirmed_orders:
        review_factory.create(order=order)

    disputed_orders = [
        order for order in orders if order.status in DISPUTED_ORDER_STATUSES
    ]
    for index, order in enumerate(disputed_orders):
        if index % DISPUTE_SAMPLE_RATE == 0:
            dispute_factory.create(order=order)

    payouts = [payout_factory.create(order=order) for order in confirmed_orders]
    return confirmed_orders, payouts


class Command(BaseCommand):
    help = (
        "Seed the local database with fake users, provider profiles, requests, "
        "offers, messages, orders, reviews, disputes, payments, and payouts."
    )

    def add_arguments(self, parser):
        parser.add_argument("--customers", type=int, default=20)
        parser.add_argument("--providers", type=int, default=5)
        parser.add_argument("--requests", type=int, default=15)
        parser.add_argument("--offers", type=int, default=20)
        parser.add_argument("--messages", type=int, default=40)

    def handle(self, *args, **options):
        if not settings.DEBUG:
            msg = "Refusing to seed data outside of DEBUG environments."
            raise CommandError(msg)

        # Imported here, not at module scope: these pull in factory-boy, a
        # dev-only dependency that isn't installed in the production image.
        from sabil_book.offers.tests.factories import MessageFactory  # noqa: PLC0415
        from sabil_book.offers.tests.factories import OfferFactory  # noqa: PLC0415
        from sabil_book.offers.tests.factories import OrderFactory  # noqa: PLC0415
        from sabil_book.payments.tests.factories import PaymentFactory  # noqa: PLC0415
        from sabil_book.payments.tests.factories import PayoutFactory  # noqa: PLC0415
        from sabil_book.requests.tests.factories import RequestFactory  # noqa: PLC0415
        from sabil_book.reviews.tests.factories import DisputeFactory  # noqa: PLC0415
        from sabil_book.reviews.tests.factories import ReviewFactory  # noqa: PLC0415
        from sabil_book.users.tests.factories import (  # noqa: PLC0415
            ProviderProfileFactory,
        )
        from sabil_book.users.tests.factories import UserFactory  # noqa: PLC0415

        n_customers = options["customers"]
        n_providers = options["providers"]
        n_requests = options["requests"]
        n_offers = options["offers"]
        n_messages = options["messages"]
        _validate_counts(n_customers, n_providers, n_requests, n_offers, n_messages)

        with transaction.atomic():
            customers = UserFactory.create_batch(n_customers)
            provider_users = UserFactory.create_batch(n_providers)
            providers = [
                ProviderProfileFactory.create(user=provider_user)
                for provider_user in provider_users
            ]

            requesters = customers + provider_users
            requests = [
                RequestFactory.create(customer=requesters[index % len(requesters)])
                for index in range(n_requests)
            ]

            # Offer has a unique constraint on (request, provider) while
            # pending/accepted, so each offer needs a distinct pair to avoid
            # intermittent seed failures.
            request_provider_pairs = list(itertools.product(requests, providers))
            random.shuffle(request_provider_pairs)
            if n_offers > len(request_provider_pairs):
                msg = (
                    f"Cannot create {n_offers} offers from only "
                    f"{len(request_provider_pairs)} distinct request/provider pairs."
                )
                raise CommandError(msg)
            offers = [
                OfferFactory.create(request=request, provider=provider)
                for request, provider in request_provider_pairs[:n_offers]
            ]

            orders = [
                OrderFactory.create(offer=offer)
                for offer in offers
                if offer.status == Offer.OfferStatus.ACCEPTED
            ]

            for index in range(n_messages):
                MessageFactory.create(
                    offer=offers[index % len(offers)],
                    sender=requesters[index % len(requesters)],
                )

            confirmed_orders, payouts = _seed_post_order_data(
                orders,
                ReviewFactory,
                PaymentFactory,
                DisputeFactory,
                PayoutFactory,
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {n_customers} customers, {n_providers} providers, "
                f"{n_requests} requests, {n_offers} offers, {n_messages} messages, "
                f"{len(orders)} orders (from accepted offers), a payment per order, "
                f"{len(confirmed_orders)} reviews and {len(payouts)} payouts for "
                f"confirmed orders, and disputes on every {DISPUTE_SAMPLE_RATE}rd "
                f"order in a dispute-related state.",
            ),
        )

from __future__ import annotations

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from sabil_book.offers.models import Offer
from sabil_book.offers.tests.factories import MessageFactory
from sabil_book.offers.tests.factories import OfferFactory
from sabil_book.offers.tests.factories import OrderFactory
from sabil_book.reviews.tests.factories import DisputeFactory
from sabil_book.reviews.tests.factories import ReviewFactory
from sabil_book.users.tests.factories import ProviderProfileFactory
from sabil_book.users.tests.factories import RequestFactory
from sabil_book.users.tests.factories import UserFactory

DISPUTE_SAMPLE_RATE = 3


class Command(BaseCommand):
    help = (
        "Seed the local database with fake users, provider profiles, requests, "
        "offers, messages, orders, reviews, and disputes."
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

        n_customers = options["customers"]
        n_providers = options["providers"]
        n_requests = options["requests"]
        n_offers = options["offers"]
        n_messages = options["messages"]

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

        offers = [
            OfferFactory.create(
                request=requests[index % len(requests)],
                provider=providers[index % len(providers)],
            )
            for index in range(n_offers)
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

        for order in orders:
            ReviewFactory.create(order=order)

        for index, order in enumerate(orders):
            if index % DISPUTE_SAMPLE_RATE == 0:
                DisputeFactory.create(order=order)

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {n_customers} customers, {n_providers} providers, "
                f"{n_requests} requests, {n_offers} offers, {n_messages} messages, "
                f"{len(orders)} orders (from accepted offers), a review per order, "
                f"and disputes on every {DISPUTE_SAMPLE_RATE}rd order.",
            ),
        )

from __future__ import annotations

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from sabil_book.users.tests.factories import ProviderProfileFactory
from sabil_book.users.tests.factories import RequestFactory
from sabil_book.users.tests.factories import UserFactory


class Command(BaseCommand):
    help = "Seed the local database with fake users, provider profiles, and requests."

    def add_arguments(self, parser):
        parser.add_argument("--customers", type=int, default=20)
        parser.add_argument("--providers", type=int, default=5)
        parser.add_argument("--requests", type=int, default=15)

    def handle(self, *args, **options):
        if not settings.DEBUG:
            msg = "Refusing to seed data outside of DEBUG environments."
            raise CommandError(msg)

        n_customers = options["customers"]
        n_providers = options["providers"]
        n_requests = options["requests"]

        customers = UserFactory.create_batch(n_customers)
        provider_users = UserFactory.create_batch(n_providers)
        for provider_user in provider_users:
            ProviderProfileFactory.create(user=provider_user)

        requesters = customers + provider_users
        for index in range(n_requests):
            RequestFactory.create(customer=requesters[index % len(requesters)])

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {n_customers} customers, {n_providers} providers "
                f"(with provider profiles), and {n_requests} requests.",
            ),
        )

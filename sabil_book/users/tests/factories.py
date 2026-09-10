from __future__ import annotations

import factory
from factory import Faker
from factory import fuzzy
from factory import post_generation
from factory.django import DjangoModelFactory

from sabil_book.users.models import ProviderProfile
from sabil_book.users.models import Request
from sabil_book.users.models import User


class UserFactory(DjangoModelFactory[User]):
    email = factory.Sequence(lambda n: f"user{n}@example.com")
    name = Faker("name")

    @post_generation
    def password(self: User, create: bool, extracted: str | None, **kwargs):  # noqa: FBT001
        password = (
            extracted
            if extracted
            else Faker(
                "password",
                length=42,
                special_chars=True,
                digits=True,
                upper_case=True,
                lower_case=True,
            ).evaluate(None, None, extra={"locale": None})
        )
        self.set_password(password)
        if create:
            self.save()

    class Meta:
        model = User
        skip_postgeneration_save = True


class ProviderProfileFactory(DjangoModelFactory[ProviderProfile]):
    user = factory.SubFactory(UserFactory)
    kyc_status = fuzzy.FuzzyChoice(ProviderProfile.KYCStatus.values)
    payout_provider = Faker("company")

    class Meta:
        model = ProviderProfile


class RequestFactory(DjangoModelFactory[Request]):
    customer = factory.SubFactory(UserFactory)
    category = fuzzy.FuzzyChoice(Request.RequestCategory.values)
    budget = fuzzy.FuzzyDecimal(10, 500, precision=2)

    class Meta:
        model = Request

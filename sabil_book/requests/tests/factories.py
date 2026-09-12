import factory
from factory import Faker
from factory import fuzzy
from factory.django import DjangoModelFactory

from sabil_book.requests.models import Request
from sabil_book.users.tests.factories import UserFactory


class RequestFactory(DjangoModelFactory[Request]):
    customer = factory.SubFactory(UserFactory)
    category = fuzzy.FuzzyChoice(Request.RequestCategory.values)
    title = Faker("sentence")
    description = Faker("paragraph")
    budget = fuzzy.FuzzyDecimal(10, 500, precision=2)

    class Meta:
        model = Request

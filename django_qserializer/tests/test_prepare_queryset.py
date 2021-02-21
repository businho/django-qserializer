import pytest

from django_qserializer import BaseSerializer
from django_qserializer.tests.testapp.models import Bus, Company


@pytest.fixture
def bus_fixture(db):
    company = Company.objects.create()
    return Bus.objects.create(company=company)


def test_manager_works(bus_fixture, db, django_assert_num_queries):
    class S(BaseSerializer):
        pass

    bus = Bus.objects.to_serialize(S).first()
    with django_assert_num_queries(1):
        bus.company


def test_select_related_attr(bus_fixture, db, django_assert_num_queries):
    class S(BaseSerializer):
        select_related = ['company']

    bus = Bus.objects.to_serialize(S).first()
    with django_assert_num_queries(0):
        bus.company


def test_prefetch_related_attr(bus_fixture, db, django_assert_num_queries):
    class S(BaseSerializer):
        prefetch_related = ['company']

    with django_assert_num_queries(2):
        # bus query + company prefetch query
        bus = Bus.objects.to_serialize(S).first()

    with django_assert_num_queries(0):
        bus.company

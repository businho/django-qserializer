import pytest

from django_qserializer import BaseSerializer
from django_qserializer.serialization import SerializableManager
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


def test_select_related_callable(bus_fixture, db, django_assert_num_queries):
    class S(BaseSerializer):
        def select_related(self):
            return ['company']

    bus = Bus.objects.to_serialize(S).first()
    with django_assert_num_queries(0):
        bus.company


def test_prefetch_related_callable(bus_fixture, db, django_assert_num_queries):
    class S(BaseSerializer):
        def prefetch_related(self):
            return ['company']

    with django_assert_num_queries(2):
        # bus query + company prefetch query
        bus = Bus.objects.to_serialize(S).first()

    with django_assert_num_queries(0):
        bus.company


def test_default_serializer_select_related(bus_fixture, db, django_assert_num_queries):
    class BusProxy(Bus):
        objects = SerializableManager(
            select_related=['company'],
        )

        class Meta:
            app_label = 'testapp'
            proxy = True

    bus = BusProxy.objects.to_serialize().first()
    with django_assert_num_queries(0):
        bus.company


def test_default_serializer_prefetch_related(bus_fixture, db, django_assert_num_queries):
    class BusProxy(Bus):
        objects = SerializableManager(
            prefetch_related=['company'],
        )

        class Meta:
            app_label = 'testapp'
            proxy = True

    with django_assert_num_queries(2):
        bus = BusProxy.objects.to_serialize().first()

    with django_assert_num_queries(0):
        bus.company

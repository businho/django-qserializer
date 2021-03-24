import pytest

from django_qserializer import BaseSerializer, serialize
from django_qserializer.tests.testapp.models import Bus, Company


@pytest.fixture
def bus_fixture(db):
    company = Company.objects.create(name='Hurricane Cart')
    return Bus.objects.create(company=company)


def test_magic_serialize_method(bus_fixture, db, django_assert_num_queries):
    class S(BaseSerializer):
        select_related = ['company']

        def serialize_object(self, bus):
            return {
                'company': bus.company.name,
            }

    bus = Bus.objects.to_serialize(S).first()
    with django_assert_num_queries(0):
        assert {'company': 'Hurricane Cart'} == bus.serialize()


def test_global_serialize(bus_fixture, db, django_assert_num_queries):
    class S(BaseSerializer):
        select_related = ['company']

        def serialize_object(self, bus):
            return {
                'company': bus.company.name,
            }

    bus = Bus.objects.to_serialize(S).first()
    with django_assert_num_queries(0):
        assert [{'company': 'Hurricane Cart'}] == list(serialize([bus]))


def test_global_serialize_empty():
    assert [] == serialize([])


def test_serialize_object_not_implemented(bus_fixture, db):
    bus = Bus.objects.to_serialize().first()
    with pytest.raises(NotImplementedError):
        bus.serialize()

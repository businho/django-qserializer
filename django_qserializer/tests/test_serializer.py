import pytest

from django_qserializer import BaseSerializer, serialize
from django_qserializer.tests.testapp.models import Bus, Company, Travel


@pytest.fixture
def bus_fixture(db):
    company = Company.objects.create(name='Hurricane Cart')
    return Bus.objects.create(company=company, plate='BUSER')


@pytest.fixture
def travel_fixture(db, bus_fixture):
    return Travel.objects.create(bus=bus_fixture)


def test_magic_serialize_method(bus_fixture, django_assert_num_queries):
    class S(BaseSerializer):
        select_related = ['company']

        def serialize_object(self, bus):
            return {
                'company': bus.company.name,
            }

    bus = Bus.objects.to_serialize(S).first()
    with django_assert_num_queries(0):
        assert {'company': 'Hurricane Cart'} == bus.serialize()


def test_global_serialize(bus_fixture, django_assert_num_queries):
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


def test_serialize_object_not_implemented(bus_fixture):
    bus = Bus.objects.to_serialize().first()
    with pytest.raises(NotImplementedError):
        bus.serialize()


def test_extras(bus_fixture, django_assert_num_queries):
    class Attr(BaseSerializer):
        select_related = ['company']

        def serialize_object(self, obj):
            return {
                'myattr': obj.company.name
            }

    def func(obj):
        return {
            'seats': 32,
        }

    class S(BaseSerializer):
        extra = {
            'myattr': Attr,
            'func': func,
        }

        def serialize_object(self, obj):
            return {
                'plate': obj.plate,
            }

    serializer = S(extra=['myattr', 'func'])

    with django_assert_num_queries(1):
        bus = Bus.objects.to_serialize(serializer).first()

    expected = {
        'plate': 'BUSER',
        'myattr': 'Hurricane Cart',
        'seats': 32,
    }

    with django_assert_num_queries(0):
        assert expected == bus.serialize()

    with django_assert_num_queries(0):
        assert expected == next(serialize([bus]))


def test_extras_recursive(bus_fixture, django_assert_num_queries):
    def city(obj):
        return {
            'city': 'SJK',
        }

    class Attr(BaseSerializer):
        extra = {
            'city': city,
        }
        select_related = ['company']

        def serialize_object(self, obj):
            return {
                'myattr': obj.company.name
            }

    class S(BaseSerializer):
        extra = {
            'myattr': Attr(extra=['city']),
        }

        def serialize_object(self, obj):
            return {
                'plate': obj.plate,
            }

    serializer = S(extra=['myattr'])

    with django_assert_num_queries(1):
        bus = Bus.objects.to_serialize(serializer).first()

    expected = {
        'plate': 'BUSER',
        'myattr': 'Hurricane Cart',
        'city': 'SJK',
    }

    with django_assert_num_queries(0):
        assert expected == bus.serialize()


def test_prepare_objects_after_prefetch(travel_fixture):
    """
    Regression test. Prior implementation ran prepare_objects before prefetchs.
    """

    class S(BaseSerializer):
        prefetch_related = ['travels']

        def prepare_objects(self, objs):
            for obj in objs:
                assert obj._prefetched_objects_cache

        def serialize_object(self, obj):
            return {
                'plate': obj.plate,
            }

    Bus.objects.to_serialize(S).first()

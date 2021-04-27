from django.db import models
from django.db.models.query import ModelIterable
from django.db.models.manager import BaseManager


class _SerializationWrapper:
    """Method wrapper to make a picklable object."""
    def __init__(self, serializer, obj):
        self.serializer = serializer
        self.obj = obj

    def __call__(self):
        return self.serializer.serialize_object(self.obj)


class BaseSerializer:
    select_related = None
    prefetch_related = None

    def __init__(self, *, select_related=None, prefetch_related=None):
        if select_related:
            self.select_related = select_related
        if prefetch_related:
            self.prefetch_related = prefetch_related

    def _prepare_queryset(self, qs):
        if self.select_related:
            if callable(self.select_related):
                qs = self.select_related(qs)
            else:
                qs = qs.select_related(*self.select_related)

        if self.prefetch_related:
            if callable(self.prefetch_related):
                qs = self.prefetch_related(qs)
            else:
                qs = qs.prefetch_related(*self.prefetch_related)

        return self.prepare_queryset(qs)

    def prepare_queryset(self, qs):
        """
        Custom change the queryset. It is possible to implement `select_related`
        and `prefetch_related` attributes with it, but they work nice together.
        """
        return qs

    def _prepare_objects(self, objs):
        self.prepare_objects(objs)
        for obj in objs:
            obj.serialize = _SerializationWrapper(self, obj)

    def prepare_objects(self, objs):
        """
        Prepare objects after they are loaded to memory.

        It is a hook to add data in bulk to loaded objects, like fetching info
        from cache and attaching to them.
        """
        pass

    def serialize_object(self, obj):
        """
        Required implementation. It converts the Django model to a serializable
        dict.

        Avoid slow calls here because it will cause N+1 issues.
        """
        raise NotImplementedError

    def serialize(self, objs):
        yield from map(self.serialize_object, objs)


class _SerializableModelIterable(ModelIterable):
    def __iter__(self):
        data = list(super().__iter__())
        self.queryset.serializer._prepare_objects(data)
        yield from data


class SerializableQuerySet(models.QuerySet):
    def _resolve_serializer(self, serializer):
        if not isinstance(serializer, BaseSerializer):
            serializer = serializer()
        return serializer

    @property
    def serializer(self):
        return getattr(self, '_serializer', None)

    def to_serialize(self, serializer=None):
        self._serializer = self._resolve_serializer(serializer)
        # https://github.com/django/django/blob/981a3426cf2f54f5282e79fb7f47726998c87cb2/django/db/models/query.py#L353
        self._iterable_class = _SerializableModelIterable
        return self._serializer._prepare_queryset(self)

    def _clone(self):
        c = super()._clone()
        c._serializer = self.serializer
        return c


class SerializableManager(BaseManager.from_queryset(SerializableQuerySet)):
    def __init__(self, *, select_related=None, prefetch_related=None,
                 default_serializer=BaseSerializer):
        super().__init__()
        self.default_serializer = default_serializer(
            select_related=select_related,
            prefetch_related=prefetch_related,
        )

    def to_serialize(self, serializer=None):
        if serializer is None:
            serializer = self.default_serializer
        return self.get_queryset().to_serialize(serializer)


def serialize(objs):
    try:
        obj = objs[0]
    except IndexError:
        return []
    serializer = obj.serialize.serializer
    return serializer.serialize(objs)

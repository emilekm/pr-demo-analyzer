from demo_analyzer.helpers import BufferError
from demo_analyzer.serializers.fields import Field, FlagsField


__all__ = [
    'SkipField',
    'Serializer',
    'ListSerializer',
]


class SkipField(Exception):
    pass


class empty:
    pass


class BaseSerializer(Field):
    _buffer = None
    _data = None

    def __init__(self, data=empty, buffer=empty, *args, **kwargs):
        if data is not empty:
            self._data = data
        if buffer is not empty:
            self._buffer = buffer
    
        kwargs.pop('many', None)
        super().__init__(**kwargs)

    @property
    def buffer(self):
        if not self._buffer and self._data:
            data = self.get_attribute(self._data)
            self._buffer = self.encode(data)

        return self._buffer

    @property
    def data(self):
        if not self._data and self._buffer:
            decoded = self.decode(self._buffer)
            self._data = self.get_value(decoded)

        return self._data

    def __new__(cls, *args, **kwargs):
        if kwargs.pop('many', False) or getattr(cls.Meta, 'many', False):
            return cls.many_init(*args, **kwargs)
        return super().__new__(cls)

    @classmethod
    def many_init(cls, *args, **kwargs):
        kwargs['child'] = cls(*args, **kwargs)
        return ListSerializer(*args, **kwargs)

    class Meta:
        many = False


class SerializerMetaclass(type):
    @classmethod
    def _get_declared_fields(cls, bases, attrs):
        fields = [
            (field_name, attrs.pop(field_name))
            for field_name, obj in list(attrs.items())
            if isinstance(obj, Field)
        ]
        fields.sort(key=lambda x: x[1]._creation_counter)

        for field_name, field in fields:
            field.bind(field_name)

        for base in reversed(bases):
            if hasattr(base, '_declared_fields'):
                fields = [
                    (field_name, obj)
                    for field_name, obj in base._declared_fields
                    if field_name not in attrs
                ] + fields

        return fields

    def __new__(cls, name, bases, attrs):
        attrs['_declared_fields'] = cls._get_declared_fields(bases, attrs)
        return super().__new__(cls, name, bases, attrs)


class Serializer(BaseSerializer,
                 metaclass=SerializerMetaclass):
    def encode(self, data):
        flags = None
        ret = []
        for field_name, field in self._declared_fields:
            if flags and flags.get(field_name) is False:
                continue

            value = field.get_attribute(data)

            if isinstance(field, FlagsField):
                flags = value

            encoded = field.encode(value)
            ret.append(encoded)

        return b''.join(ret)

    def decode(self, buffer):
        flags = None
        ret = {}
        for field_name, field in self._declared_fields:
            if flags and getattr(flags, field.flag) is False:
                continue

            try:
                raw_value = field.decode(buffer)
            except BufferError:
                break

            validate_method = getattr(self, f'validate_{field_name}', None)
            if validate_method:
                try:
                    validate_method(raw_value, ret)
                except SkipField:
                    buffer.seek(-field.size, 1)
                    continue

            value = field.get_value(raw_value)
            ret[field_name] = value

            if isinstance(field, FlagsField):
                flags = value

        return ret


class ListSerializer(BaseSerializer):
    child = None

    def __init__(self, *args, **kwargs):
        self.child = kwargs.pop('child', self.child)
        super().__init__(*args, **kwargs)

    def encode(self, data):
        ret = []
        for d in data:
            value = self.child.encode(d)
            ret.append(value)

        return b''.join(ret)

    def decode(self, buffer):
        ret = []
        while True:
            value = self.child.decode(buffer)
            if not value:
                break
            ret.append(value)
        return ret

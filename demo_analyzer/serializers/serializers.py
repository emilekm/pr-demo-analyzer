from demo_analyzer.serializers import fields

Field = fields.Field


class BaseSerializer(fields.Field):
    def __new__(cls, *args, **kwargs):
        if kwargs.pop('many', False):
            return cls.many_init(*args, **kwargs)
        return super().__new__(cls)

    @classmethod
    def many_init(cls, *args, **kwargs):
        kwargs['child'] = cls(*args, **kwargs)
        return ListSerializer(*args, **kwargs)


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
        ret = []
        for field_name, field in self._declared_fields:
            value = field.get_attribute(data)
            encoded = field.encode(value)
            ret.append(encoded)

        return b''.join(ret)

    def decode(self, buffer):
        ret = {}
        for field_name, field in self._declared_fields:
            try:
                raw_value = field.decode(buffer)
                ret[field_name] = field.get_value(raw_value)
            except ValueError:
                break
        return ret


class FlagedSerializer(Serializer):
    def encode(self, data):
        ret = []
        for field_name, field in self._declared_fields:
            if isinstance(field, fields.Field):
                flags = data.get(field_name, None)
                if flags is None:
                    flags = self._generate_flags(data)

            if flags and flags.get(field_name) is False:
                continue

            value = field.encode(data.get(field_name))

            ret.append(value)

        return b''.join(ret)

    def decode(self, buffer):
        flags = None
        ret = {}
        for field_name, field in self._declared_fields:
            if flags and getattr(flags, field.flag) is False:
                continue

            value = field.decode(buffer)

            if isinstance(field, fields.Field):
                flags = value

            ret[field_name] = value
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

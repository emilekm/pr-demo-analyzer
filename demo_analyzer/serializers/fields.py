from datetime import datetime, timezone
from functools import partial
import struct


class Field:
    _creation_counter = 0

    def __init__(self, flag=None):
        self._creation_counter = Field._creation_counter
        Field._creation_counter += 1

        self.flag = flag

        self.field_name = None

    def bind(self, field_name):
        self.field_name = field_name

        if self.flag is None:
            self.flag = field_name


    def get_attribute(self, data):
        return data[self.field_name]

    def encode(self, value):
        raise NotImplementedError

    def get_value(self, raw_value):
        return raw_value

    def decode(self, buffer):
        raise NotImplementedError


FMT_BYTE_ORDERS = ('@', '=', '<', '>', '!')


class StructField(Field):
    fmt = None
    size = None

    def __init__(self, fmt=None, **kwargs):
        super().__init__(**kwargs)

        if fmt:
            self.fmt = fmt

        if self.fmt[0] not in FMT_BYTE_ORDERS:
            self.fmt = '<' + self.fmt

        self.size = struct.calcsize(self.fmt)


    def encode(self, value):
        return struct.pack(
            self.fmt,
            value
        )

    def decode(self, buffer):
        return struct.unpack(
            self.fmt,
            buffer.read(self.size)
        )[0]


BYTE = 'c'


class ByteField(StructField):
    fmt = BYTE


INT8 = 'b'
UINT8 = 'B'


class Int8Field(StructField):
    fmt = INT8


class UInt8Field(StructField):
    fmt = UINT8


INT16 = 'h'
UINT16 = 'H'


class Int16Field(StructField):
    fmt = INT16


class UInt16Field(StructField):
    fmt = UINT16


INT32 = 'i'
UINT32 = 'I'


class Int32Field(StructField):
    fmt = INT32


class UInt32Field(StructField):
    fmt = UINT32


INT64 = 'q'
UINT64 = 'Q'


class Int64Field(StructField):
    fmt = INT64


class UInt64Field(StructField):
    fmt = UINT64


FLOAT = 'f'


class FloatField(StructField):
    fmt = FLOAT


BOOL = '?'


class BoolField(StructField):
    fmt = BOOL


class TimestampField(StructField):
    def get_attribute(self, data):
        return super().get_attribute(data).timestamp()

    def get_value(self, raw_value):
        return datetime.fromtimestamp(raw_value, timezone.utc)


class StringField(Field):
    @staticmethod
    def encode(value):
        return value + '\x00'

    @staticmethod
    def decode(buffer):
        slist = []

        while True:
            try:
                val = buffer.read(1)[0]
            except ValueError:
                break
            if val == 0:
                break
            slist.append(chr(val))

        return ''.join(slist)


class FlagsField(StructField):
    def __init__(self, flags, **kwargs):
        super().__init__(**kwargs)

        self.flags = flags

    def get_attribute(self, data):
        try:
            flags = super().get_attribute(data)
        except KeyError:
            pass
        else:
            flags = self.generate_flags(data)

        return sum(
            [getattr(self.flags, name) for name, value in flags if value is True]
        )

    def get_value(self, raw_value):
        return {
            name: self.bitwise_check(raw_value, member)
            for name, member in self.flags.__members__.items()
        }

    def generate_flags(self, data):
        return {
            name: True if data[name] is not None else False
            for name in self.flags.__members__
        }

    @staticmethod
    def bitwise_check(bits, bit_to_check):
        return True if (bits & bit_to_check) == bit_to_check else False

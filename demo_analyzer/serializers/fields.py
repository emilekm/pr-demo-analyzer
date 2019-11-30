from datetime import datetime
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

    def decode(self, buffer, pos):
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
        ), self.size

    def decode(self, buffer, pos):
        new_pos = pos + self.size
        return struct.unpack(
            self.fmt,
            buffer[pos:new_pos]
        )[0], new_pos


class ByteField(StructField):
    fmt = 'c'


class Int8Field(StructField):
    fmt = 'b'


class UInt8Field(StructField):
    fmt = 'B'


class Int16Field(StructField):
    fmt = 'h'


class UInt16Field(StructField):
    fmt = 'H'


class Int32Field(StructField):
    fmt = 'i'


class UInt32Field(StructField):
    fmt = 'I'


class Int64Field(StructField):
    fmt = 'q'


class UInt64Field(StructField):
    fmt = 'Q'


class FloatField(StructField):
    fmt = 'f'


class BoolField(StructField):
    fmt = '?'


class TimestampField(StructField):
    def get_attribute(self, data):
        return super().get_attribute(data).timestamp()

    def get_value(self, raw_value):
        return datetime.fromtimestamp(raw_value)


class StringField(Field):
    @staticmethod
    def encode(value):
        return value + '\x00', len(value) + 1

    @staticmethod
    def decode(buffer, pos):
        length = len(buffer)
        slist = []

        while pos < length:
            val = buffer[pos]
            pos += 1
            if val == 0:
                break
            slist.append(chr(val))

        return ''.join(slist), pos


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

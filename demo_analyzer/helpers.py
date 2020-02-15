import struct


class DataView:
    __slots__ = ('buffer', 'pos', 'size')

    def __init__(self, buffer, pos, size):
        self.buffer = buffer
        self.pos = pos
        self.size = size

    def __len__(self):
        return self.size

    def _get_slice(self, arg):
        assert not arg.step, (
            '{} does not support slicing with steps'.format(self.__class__.__name__)
        )

        start = arg.start
        stop = arg.stop

        pos = self.pos
        size = self.size

        if stop is not None and stop < size:
            size = stop

        if start is not None:
            pos = pos + start
            size = size - start

        return self.__class__(self.buffer, pos, size)

    def __getitem__(self, arg):
        if isinstance(arg, slice):
            return self._get_slice(arg)

        if arg >= self.size:
            raise IndexError

        return self.buffer[self.pos+arg]


class DemoView(DataView):
    def iter_messages(self):
        pos = 0
        buffer_length = len(self)

        while buffer_length > pos:
            size = struct.unpack('<H', self.buffer[pos:pos+2])
            pos = pos + 2

            if pos + size > buffer_length:
                break


            yield pos, size

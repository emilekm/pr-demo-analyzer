import struct
from io import IOBase
from zlib import decompress


class DataView(IOBase):
    __slots__ = ('_buffer', '_initial_pos', '_relative_pos', '_size')

    def __init__(self, buffer, pos=0, size=-1):
        self._buffer = buffer
        self._initial_pos = pos
        self._relative_pos = 0
        if size == -1:
            size = len(buffer) - pos
        self._size = size

    @property
    def _absolute_pos(self):
        return self._initial_pos + self._relative_pos

    def seek(self, pos, whence=0):
        if whence == 0:
            if pos < 0:
                raise ValueError("negative seek position %r" % (pos,))
            self._relative_pos = pos
        elif whence == 1:
            self._relative_pos = max(0, self._relative_pos + pos)
        elif whence == 2:
            self._relative_pos = max(0, self._size + pos)
        else:
            raise ValueError("unsupported whence value")
        return self._relative_pos

    def peek(self, size=1):
        size = min(self._size - self._relative_pos, size)
        return self._buffer[self._absolute_pos:self._absolute_pos + size]

    def seekable(self):
        return True

    def readable(self):
        if self._absolute_pos < self._initial_pos+self._size:
            return True
        return False

    def read(self, size=1):
        size = min(self._size - self._relative_pos, size)
        pos = self._absolute_pos
        self.seek(size, 1)
        return self._buffer[pos:pos+size]

    def getbuffer(self):
        return self._buffer

    def getvalue(self):
        return self._buffer[self._initial_pos:self._initial_pos+self._size]

    def __bytes__(self):
        return self.getvalue()


class DemoView(DataView):
    def readmessage(self):
        msg_size, = struct.unpack('<H', self.read(2))
        pos = self._absolute_pos
        self.seek(msg_size, 1)
        return DataView(self._buffer, pos, msg_size)

    def readmessages(self):
        while self.readable():
            yield self.readmessage()

    def __iter__(self):
        return self.readmessages()

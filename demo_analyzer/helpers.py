import struct
from io import IOBase
from zlib import decompress


from demo_analyzer import constants


class BufferError(Exception):
    pass


class DataView(IOBase):
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

    def _check_enough_bytes(self, size):
        if (self._relative_pos + size) > self._size:
            raise BufferError('not enough bytes')

    def seek(self, pos, whence=0):
        if whence == 0:
            if pos < 0:
                raise ValueError(f'negative seek position {pos}')
            if pos >= self._size:
                raise ValueError(f'seek beyond buffer size {pos}')
            self._relative_pos = pos
        elif whence == 1:
            self._relative_pos = max(0, self._relative_pos + pos)
        elif whence == 2:
            self._relative_pos = max(0, self._size + pos)
        else:
            raise ValueError('unsupported whence value')
        return self._relative_pos

    def peek(self, size=1):
        self._check_enough_bytes(size)
        return self._buffer[self._absolute_pos:self._absolute_pos + size]

    def read(self, size=1):
        ret = self.peek(size)
        self.seek(size, 1)
        return ret

    def getbuffer(self):
        return self._buffer

    def getvalue(self):
        self._buffer = self._buffer[self._initial_pos:self._initial_pos+self._size]
        self._initial_pos = 0
        return self._buffer

    def __bytes__(self):
        return self.getvalue()


class MessageView(DataView):
    type = None

    def __init__(self, buffer, pos=0, size=-1, with_type=True):
        super().__init__(buffer, pos, size)
        if with_type is True:
            self.type = message_type(self)


class DemoView(DataView):
    def readmessage(self):
        try:
            msg_size, = struct.unpack('<H', self.read(2))
            self._check_enough_bytes(msg_size)
        except BufferError:
            return
        pos = self._absolute_pos
        self.seek(msg_size, 1)
        return MessageView(self.getbuffer(), pos, msg_size)

    def __next__(self):
        message = self.readmessage()
        if not message:
            raise StopIteration
        return message

    def __iter__(self):
        return self


def open_demo(filename):
    with open(filename, 'rb') as f:
        buffer = decompress(f.read())
    return DemoView(buffer)


def message_type(message):
    msg_type, = struct.unpack('<c', message.read(1))
    return constants.MessageTypes(msg_type)

from zlib import decompress

from demo_analyzer import messages
from demo_analyzer.analyzer import analyzer, emit, listen, Event
from demo_analyzer.runner import Runner


@emit('new_file')
@emit('end_of_file')
def file_opener(filename, event):
    with open(filename, 'rb') as f:
        buffer = decompress(f.read())
    yield buffer, 'new_file'
    yield None, 'end_of_file'


@emit('message')
@listen(file_opener, 'new_file')
def file_parser(buffer, event):
    pos = 0
    buffer_length = len(buffer)

    serializer = messages.Header()

    while buffer_length > pos:
        header, pos = serializer.decode(buffer, pos)
        message_length = header.get('length')
        new_pos = pos + message_length

        if not message_length or new_pos > buffer_length:
            break

        yield buffer[pos:new_pos], 'message'

        pos = new_pos



@listen(file_parser, 'message')
@emit('server_details')
@emit('kill')
@emit('ticks')
def message_dispatcher(buffer, event):
    serializer = messages.Type()
    msg_type, size = serializer.decode(buffer, 0)
    if msg_type['type'] == b'\x00':
        return buffer[size:], 'server_details'
    elif msg_type['type'] == b'\x50':
        return buffer[size:], 'kill'
    elif msg_type['type'] == b'\xf1':
        return buffer[size:], 'ticks'


@listen(message_dispatcher, 'server_details')
@emit('print')
def server_details(buffer, event):
    serializer = messages.ServerDetails()
    print(serializer.decode(buffer, 0))
    return None, 'print'


if __name__ == "__main__":
    import sys

    start = Event(file_opener, 'new_file')
    ends = [Event(server_details, 'print')]
    runner = Runner(start, ends)
    runner(sys.argv[1])

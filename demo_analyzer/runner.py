import inspect
from collections import defaultdict


class DependencyError(Exception):
    '''
    Raised when graph traversing reaches end different than speciefied
    '''


class Runner:
    __slots__ = (
        'start',
        '_graph',
    )

    @classmethod
    def _make_graph(cls, start, ends, _graph=defaultdict(list)):
        for end in ends:
            if end in _graph or start == end:
                continue

            events = end.connections()
            if len(events) == 0:
                raise DependencyError

            for event in events:
                _graph[end].append(event)

            cls._make_graph(start, events, _graph=_graph)

        return _graph

    @classmethod
    def _reverse_graph(cls, graph):
        new_graph = defaultdict(list)
        for event, nodes in graph.items():
            for node in nodes:
                new_graph[node].append(event)

        return new_graph

    def __init__(self, start, ends):
        self.start = start

        graph = self._make_graph(start, ends)
        self._graph = self._reverse_graph(graph)

    def _handle_events(self, listeners, data, event=None):
        for listener in listeners:
            analyzer = listener.analyzer

            returned = analyzer(data, event)

            if inspect.isgenerator(returned):
                for data in returned:
                    self._handle_events(self._graph[listener], data[0], listener)
            else:
                self._handle_events(self._graph[listener], returned[0], listener)

    def __call__(self, data):
        self._handle_events([self.start], data)

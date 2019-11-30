import inspect
from collections import defaultdict, namedtuple
from itertools import chain

__all__ = [
    'analyzer',
    'emit',
    'listen',
    'storage',
]


# Analyzer params attribute name
_ANALYZER = '_analyzer'


def _get_params(obj):
    return getattr(obj, _ANALYZER)


class Event(namedtuple('Event', 'analyzer, event_name')):
    __slots__ = () # Avoid creating instance dict
    _events = []

    def __new__(cls, *args, **kwargs):
        # Return one instance for same arguments (saves memory)
        event = super().__new__(cls, *args, **kwargs)
        try:
            index = cls._events.index(event)
            event = cls._events[index]
        except ValueError:
            cls._events.append(event)
        return event

    def connections(self):
        return _get_params(self.analyzer).connections(self.event_name)

    def __repr__(self):
        return '{name}@{analyzer}'.format(
            name=self.event_name,
            analyzer=self.analyzer.__name__,
        )


############
# Analyzer #
############


class _AnalyzerConfig:
    __slots__ = ('_emits', '_listens',)

    def __init__(self):
        self._emits = set()
        self._listens = set()

    def emit(self, event_name):
        self._emits.add(event_name)

    def listen(self, event):
        self._listens.add(event)

    @property
    def emits(self):
        return self._emits

    @property
    def listens(self):
        return self._listens

    def connections(self, event_name):
        return self.listens


def analyzer(_func=None, emits=[], listens=[]):
    '''
    Analyzer is a function that receives and emits data through events
    '''
    def decorator(func):
        params = _AnalyzerConfig()
        for event_name in emits:
            params.emit(event_name)
        for event in listens:
            if not isinstance(event, Event):
                event = Event._make(event)
            params.listen(event)
        setattr(func, _ANALYZER, params)
        return func

    # If _func is not passed as first argument, nest the decorator
    if _func is None:
        return decorator

    return decorator(_func)


def _is_analyzer(obj):
    try:
        params = _get_params(obj)
        return isinstance(params, _AnalyzerConfig)
    except AttributeError:
        return False


# Helper Analyzer decorators


def _common_decorator(registry, value):
    def decorator(func):
        if not _is_analyzer(func):
            func = analyzer(func)
        getattr(_get_params(func), registry)(value)
        return func
    return decorator


def emit(event_name):
    '''
    Adds `event_name` to emited events list
    Decorates with `analyzer` decorator (if isn't already)
    '''
    return _common_decorator('emit', event_name)


def listen(analyzer_, event_name):
    '''
    Adds Event to list of listened events
    Decorates with `analyzer` decorator (if isn't already)
    '''
    return _common_decorator('listen', Event(analyzer_, event_name))


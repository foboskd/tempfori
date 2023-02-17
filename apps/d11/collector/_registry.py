__all__ = [
    'registry',
]


class GrabberRegistry(dict):
    def register(self, what=None):
        def wrap(what):
            self[what.__name__] = what
            return what

        if callable(what):
            self[what.__name__] = what
            return wrap(what)

        return wrap


registry = GrabberRegistry()

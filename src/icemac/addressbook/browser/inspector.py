class Inspector(object):
    """Inspect the current view or object."""

    def show_context(self):
        yield {'key': 'context',
               'value': self.context}
        yield {'key': 'class of context',
               'value': self.context.__class__}
        yield {'key': 'base classes of context',
               'value': self.context.__class__.__bases__}

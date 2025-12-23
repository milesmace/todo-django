from django.template import Context
from django.template import Template as DjangoTemplate


class DBEmailTemplate:
    def __init__(self, source, engine, metadata=None):
        self.source = source
        self.engine = engine
        self.metadata = metadata or {}

        # Use Django's built-in template engine to render
        self._template = DjangoTemplate(source)

    def render(self, context=None, request=None):
        context = context or {}

        if not isinstance(context, Context):
            context = Context(context)

        return self._template.render(context)

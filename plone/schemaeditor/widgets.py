from zope.interface import Interface
from zope import schema
from plone.autoform.interfaces import WIDGETS_KEY
from plone.autoform.widgets import ParameterizedWidget
from plone.schemaeditor import SchemaEditorMessageFactory as _


class ITextWidgetParameters(Interface):

    rows = schema.Int(
        title=_(u'Rows'),
        default=5,
    )


def get_text_widget_schema(schema_context, field):
    return ITextWidgetParameters


class ISelectWidgetParameters(Interface):

    size = schema.Int(
        title=_(u'Size'),
        default=5,
    )


def get_select_widget_schema(schema_context, field):
    return ISelectWidgetParameters


# TODO:
# - avoid drive-by creation of ParameterizedFieldWidget


class WidgetSettingsAdapter(object):

    def __init__(self, field):
        self.field = field

    @property
    def widget_factory(self):
        widgets = self.field.interface.queryTaggedValue(WIDGETS_KEY, {})
        widget_factory = widgets.get(self.field.__name__)
        if widget_factory is None:
            widget_factory = ParameterizedWidget(None)
            widgets[self.field.__name__] = widget_factory
            self.field.interface.setTaggedValue(WIDGETS_KEY, widgets)
            return widget_factory
        elif isinstance(widget_factory, ParameterizedWidget):
            return widget_factory
        else:
            raise ValueError('Unrecognized widget factory')

    def __getattr__(self, name):
        if name in self.schema:
            return self.widget_factory.params.get(
                name, self.schema[name].default)
        raise AttributeError(name)

    def __setattr__(self, name, value):
        if name in self.schema:
            self.widget_factory.params[name] = value
        return object.__setattr__(self, name, value)


class TextWidgetParameters(WidgetSettingsAdapter):
    schema = ITextWidgetParameters


class SelectWidgetParameters(WidgetSettingsAdapter):
    schema = ISelectWidgetParameters

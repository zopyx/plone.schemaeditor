from zope.interface import Interface
from zope import schema
from plone.autoform.interfaces import WIDGETS_KEY
from plone.autoform.widgets import ParameterizedWidget
from plone.schemaeditor import SchemaEditorMessageFactory as _
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm


class ITextWidgetParameters(Interface):

    rows = schema.Int(
        title=_(u'Rows'),
        default=5,
    )


def get_text_widget_schema(schema_context, field):
    return ITextWidgetParameters



select_styles = SimpleVocabulary(
    [SimpleTerm(value=u'auto', title=_(u'Auto')),
     SimpleTerm(value=u'select', title=_(u'Selection Box')),
     SimpleTerm(value=u'individual', title=_(u'Checkboxes'))]
    )


class ISelectWidgetParameters(Interface):

    input_format = schema.Choice(
        title=_(u'Input Format'),
        description=_(
            "Determines whether choices are displayed in a single "
            "control or several individual controls. "
            "Choose 'auto' to use single controls for small "
            "numbers of items and a select box for more."
            ),
        vocabulary=select_styles,
        default=_(u'auto'),
    )

    size = schema.Int(
        title=_(u'Size'),
        description=_(u'Rows to display in selection boxes'),
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

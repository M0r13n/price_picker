from wtforms.ext.sqlalchemy.fields import QuerySelectMultipleField
from wtforms.widgets import ListWidget, CheckboxInput


class MultiCheckboxField(QuerySelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()

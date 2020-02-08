import marshmallow
from marshmallow import fields

MARSHMALLOW_VERSION_INFO = tuple(
    [int(part) for part in marshmallow.__version__.split(".") if part.isdigit()]
)


def unpack(return_value):
    return return_value.data if MARSHMALLOW_VERSION_INFO[0] < 3 else return_value


class MyDateField(fields.Date):
    pass

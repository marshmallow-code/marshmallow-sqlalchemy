import importlib.metadata

from .convert import (
    ModelConverter,
    column2field,
    field_for,
    fields_for_model,
    property2field,
)
from .exceptions import ModelConversionError
from .schema import (
    SQLAlchemyAutoSchema,
    SQLAlchemyAutoSchemaOpts,
    SQLAlchemySchema,
    SQLAlchemySchemaOpts,
    auto_field,
)

# TODO: Deprecate __version__
__version__ = importlib.metadata.version("marshmallow-sqlalchemy")
__all__ = [
    "SQLAlchemySchema",
    "SQLAlchemyAutoSchema",
    "SQLAlchemySchemaOpts",
    "SQLAlchemyAutoSchemaOpts",
    "auto_field",
    "ModelConverter",
    "fields_for_model",
    "property2field",
    "column2field",
    "ModelConversionError",
    "field_for",
]

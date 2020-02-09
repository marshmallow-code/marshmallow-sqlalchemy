from marshmallow.fields import FieldABC
from marshmallow.schema import Schema, SchemaMeta, SchemaOpts

from ..convert import ModelConverter
from ..exceptions import IncorrectSchemaTypeError


# This isn't really a field. It's a placeholder for the metaclass.
class SQLAlchemyAutoField(FieldABC):
    def __init__(self, *, column_name=None, model=None, table=None, field_kwargs):
        if model and table:
            raise ValueError("Cannot pass both `model` and `table` options.")

        self.column_name = column_name
        self.model = model
        self.table = table
        self.field_kwargs = field_kwargs

    def create_field(self, schema_opts, column_name, converter):
        model = self.model or schema_opts.model
        if model:
            return converter.field_for(model, column_name, **self.field_kwargs)
        else:
            table = self.table or schema_opts.table
            column = getattr(table.columns, column_name)
            return converter.column2field(column, **self.field_kwargs)

    # This field should never be bound to a schema.
    # If this method is called, it's probably because the schema is not a SQLAlchemySchema.
    def _bind_to_schema(self, field_name, schema):
        raise IncorrectSchemaTypeError(
            f"Cannot bind SQLAlchemyAutoField. Make sure that {schema} is a SQLAlchemySchema or SQLAlchemyAutoSchema."
        )

    _add_to_schema = _bind_to_schema  # marshmallow 2 compat


class SQLAlchemySchemaOpts(SchemaOpts):
    def __init__(self, meta, *args, **kwargs):
        super().__init__(meta, *args, **kwargs)

        self.sqla_session = getattr(meta, "sqla_session", None)
        self.include_fk = getattr(meta, "include_fk", False)
        self.model_converter = getattr(meta, "model_converter", ModelConverter)
        self.model = getattr(meta, "model", None)
        self.table = getattr(meta, "table", None)
        if self.model and self.table:
            raise ValueError("Cannot set both `model` and `table` options.")


class SQLAlchemySchemaMeta(SchemaMeta):
    @classmethod
    def get_declared_fields(mcs, klass, cls_fields, inherited_fields, dict_cls):
        opts = klass.opts
        Converter = opts.model_converter
        converter = Converter(schema_cls=klass)
        fields = super().get_declared_fields(
            klass, cls_fields, inherited_fields, dict_cls
        )
        fields.update(mcs.get_declared_sqla_fields(fields, converter, opts, dict_cls))
        fields.update(mcs.get_auto_fields(fields, converter, opts, dict_cls))
        return fields

    @classmethod
    def get_declared_sqla_fields(mcs, base_fields, converter, opts, dict_cls):
        return {}

    @classmethod
    def get_auto_fields(mcs, fields, converter, opts, dict_cls):
        return dict_cls(
            {
                field_name: field.create_field(
                    opts, field.column_name or field_name, converter
                )
                for field_name, field in fields.items()
                if isinstance(field, SQLAlchemyAutoField)
                and field_name not in opts.exclude
            }
        )


class SQLAlchemyAutoSchemaMeta(SQLAlchemySchemaMeta):
    @classmethod
    def get_declared_sqla_fields(cls, base_fields, converter, opts, dict_cls):
        fields = dict_cls()
        if opts.table is not None:
            fields.update(
                converter.fields_for_table(
                    opts.table,
                    fields=opts.fields,
                    exclude=opts.exclude,
                    include_fk=opts.include_fk,
                    base_fields=base_fields,
                    dict_cls=dict_cls,
                )
            )
        elif opts.model is not None:
            fields.update(
                converter.fields_for_model(
                    opts.model,
                    fields=opts.fields,
                    exclude=opts.exclude,
                    include_fk=opts.include_fk,
                    base_fields=base_fields,
                    dict_cls=dict_cls,
                )
            )
        return fields


class SQLAlchemySchema(Schema, metaclass=SQLAlchemySchemaMeta):
    """Schema for a SQLAlchemy model or table.
    Use together with `auto_field` to generate fields from columns.
    """

    OPTIONS_CLASS = SQLAlchemySchemaOpts


class SQLAlchemyAutoSchema(SQLAlchemySchema, metaclass=SQLAlchemyAutoSchemaMeta):
    """Schema that automatically generates fields from the columns of
     a SQLAlchemy model or table.
     """


def auto_field(column_name=None, *, model=None, table=None, **kwargs):
    """Mark a field to autogenerate from a model or table.

    :param column_name: Name of the column to generate the field from.
        If ``None``, matches the field name. If ``attribute`` is unspecified,
        ``attribute`` will be set to the same value as ``column_name``.
    :param model: Model to generate the field from.
        If ``None``, uses ``model`` specified on ``class Meta``.
    :param table: Table to generate the field from.
        If ``None``, uses ``table`` specified on ``class Meta``.
    :param kwargs: Field argument overrides.
    """
    if column_name is not None:
        kwargs.setdefault("attribute", column_name)
    return SQLAlchemyAutoField(
        column_name=column_name, model=model, table=table, field_kwargs=kwargs
    )

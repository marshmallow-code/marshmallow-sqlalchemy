import pytest

from marshmallow import validate, ValidationError, Schema
import marshmallow
import sqlalchemy as sa

from marshmallow_sqlalchemy import SQLAlchemySchema, SQLAlchemyAutoSchema, auto_field
from marshmallow_sqlalchemy.exceptions import IncorrectSchemaTypeError
from .utils import unpack, MARSHMALLOW_VERSION_INFO


# -----------------------------------------------------------------------------


@pytest.fixture
def teacher(models, session):
    school = models.School(id=42, name="Univ. Of Whales")
    teacher_ = models.Teacher(
        id=24, full_name="Teachy McTeachFace", current_school=school
    )
    session.add(teacher_)
    session.flush()
    return teacher_


class EntityMixin:
    id = auto_field(dump_only=True)


# Auto schemas with default options


@pytest.fixture
def sqla_auto_model_schema(models, request):
    class TeacherSchema(SQLAlchemyAutoSchema):
        class Meta:
            model = models.Teacher
            strict = True  # marshmallow 2 compat

        full_name = auto_field(validate=validate.Length(max=20))

    return TeacherSchema()


@pytest.fixture
def sqla_auto_table_schema(models, request):
    class TeacherSchema(SQLAlchemyAutoSchema):
        class Meta:
            table = models.Teacher.__table__
            strict = True  # marshmallow 2 compat

        full_name = auto_field(validate=validate.Length(max=20))

    return TeacherSchema()


# Schemas with relationships


@pytest.fixture
def sqla_schema_with_relationships(models, request):
    class TeacherSchema(EntityMixin, SQLAlchemySchema):
        class Meta:
            model = models.Teacher
            strict = True  # marshmallow 2 compat

        full_name = auto_field(validate=validate.Length(max=20))
        current_school = auto_field()
        substitute = auto_field()

    return TeacherSchema()


@pytest.fixture
def sqla_auto_model_schema_with_relationships(models, request):
    class TeacherSchema(SQLAlchemyAutoSchema):
        class Meta:
            model = models.Teacher
            include_relationships = True
            strict = True  # marshmallow 2 compat

        full_name = auto_field(validate=validate.Length(max=20))

    return TeacherSchema()


# Schemas with foreign keys


@pytest.fixture
def sqla_schema_with_fks(models, request):
    class TeacherSchema(EntityMixin, SQLAlchemySchema):
        class Meta:
            model = models.Teacher
            strict = True  # marshmallow 2 compat

        full_name = auto_field(validate=validate.Length(max=20))
        current_school_id = auto_field()

    return TeacherSchema()


@pytest.fixture
def sqla_auto_model_schema_with_fks(models, request):
    class TeacherSchema(SQLAlchemyAutoSchema):
        class Meta:
            model = models.Teacher
            include_fk = True
            include_relationships = False
            strict = True  # marshmallow 2 compat

        full_name = auto_field(validate=validate.Length(max=20))

    return TeacherSchema()


# -----------------------------------------------------------------------------


@pytest.mark.parametrize(
    "schema",
    (
        pytest.lazy_fixture("sqla_schema_with_relationships"),
        pytest.lazy_fixture("sqla_auto_model_schema_with_relationships"),
    ),
)
def test_dump_with_relationships(teacher, schema):
    assert unpack(schema.dump(teacher)) == {
        "id": teacher.id,
        "full_name": teacher.full_name,
        "current_school": 42,
        "substitute": None,
    }


@pytest.mark.parametrize(
    "schema",
    (
        pytest.lazy_fixture("sqla_schema_with_fks"),
        pytest.lazy_fixture("sqla_auto_model_schema_with_fks"),
    ),
)
def test_dump_with_foreign_keys(teacher, schema):
    assert unpack(schema.dump(teacher)) == {
        "id": teacher.id,
        "full_name": teacher.full_name,
        "current_school_id": 42,
    }


def test_table_schema_dump(teacher, sqla_auto_table_schema):
    assert unpack(sqla_auto_table_schema.dump(teacher)) == {
        "id": teacher.id,
        "full_name": teacher.full_name,
    }


@pytest.mark.parametrize(
    "schema",
    (
        pytest.lazy_fixture("sqla_schema_with_relationships"),
        pytest.lazy_fixture("sqla_schema_with_fks"),
        pytest.lazy_fixture("sqla_auto_model_schema"),
        pytest.lazy_fixture("sqla_auto_table_schema"),
    ),
)
def test_load(schema):
    assert unpack(schema.load({"full_name": "Teachy T"})) == {"full_name": "Teachy T"}


@pytest.mark.parametrize(
    "schema",
    (
        pytest.lazy_fixture("sqla_schema_with_relationships"),
        pytest.lazy_fixture("sqla_schema_with_fks"),
        pytest.lazy_fixture("sqla_auto_model_schema"),
        pytest.lazy_fixture("sqla_auto_table_schema"),
    ),
)
def test_load_validation_errors(schema):
    with pytest.raises(ValidationError):
        schema.load({"full_name": "x" * 21})


def test_auto_field_on_plain_schema_raises_error():
    class BadSchema(Schema):
        name = auto_field()

    with pytest.raises(IncorrectSchemaTypeError):
        BadSchema()


def test_cannot_set_both_model_and_table(models):
    with pytest.raises(ValueError, match="Cannot set both"):

        class BadWidgetSchema(SQLAlchemySchema):
            class Meta:
                model = models.Teacher
                table = models.Teacher


def test_passing_model_to_auto_field(models, teacher):
    class TeacherSchema(SQLAlchemySchema):
        current_school_id = auto_field(model=models.Teacher)

    schema = TeacherSchema()
    assert unpack(schema.dump(teacher)) == {
        "current_school_id": teacher.current_school_id
    }


def test_passing_table_to_auto_field(models, teacher):
    class TeacherSchema(SQLAlchemySchema):
        current_school_id = auto_field(table=models.Teacher.__table__)

    schema = TeacherSchema()
    assert unpack(schema.dump(teacher)) == {
        "current_school_id": teacher.current_school_id
    }


# https://github.com/marshmallow-code/marshmallow-sqlalchemy/issues/190
def test_auto_schema_skips_synonyms(models):
    class TeacherSchema(SQLAlchemyAutoSchema):
        class Meta:
            model = models.Teacher
            include_fk = True

    schema = TeacherSchema()
    assert "current_school_id" in schema.fields
    assert "curr_school_id" not in schema.fields


def test_auto_field_works_with_synonym(models):
    class TeacherSchema(SQLAlchemyAutoSchema):
        class Meta:
            model = models.Teacher
            include_fk = True

        curr_school_id = auto_field()

    schema = TeacherSchema()
    assert "current_school_id" in schema.fields
    assert "curr_school_id" in schema.fields


class TestAliasing:
    @pytest.fixture
    def aliased_schema(self, models):
        class TeacherSchema(SQLAlchemySchema):
            class Meta:
                model = models.Teacher
                strict = True  # marshmallow 2 compat

            # Generate field from "full_name", pull from "full_name" attribute, output to "name"
            name = auto_field("full_name")

        return TeacherSchema()

    @pytest.fixture
    def aliased_auto_schema(self, models):
        class TeacherSchema(SQLAlchemyAutoSchema):
            class Meta:
                model = models.Teacher
                exclude = ("full_name",)
                strict = True  # marshmallow 2 compat

            # Generate field from "full_name", pull from "full_name" attribute, output to "name"
            name = auto_field("full_name")

        return TeacherSchema()

    @pytest.fixture
    def aliased_attribute_schema(self, models):
        class TeacherSchema(SQLAlchemySchema):
            class Meta:
                model = models.Teacher
                strict = True  # marshmallow 2 compat

            # Generate field from "full_name", pull from "fname" attribute, output to "name"
            name = auto_field("full_name", attribute="fname")

        return TeacherSchema()

    @pytest.mark.parametrize(
        "schema",
        (
            pytest.lazy_fixture("aliased_schema"),
            pytest.lazy_fixture("aliased_auto_schema"),
        ),
    )
    def test_passing_column_name(self, schema, teacher):
        assert schema.fields["name"].attribute == "full_name"
        dumped = unpack(schema.dump(teacher))
        assert dumped["name"] == teacher.full_name

    def test_passing_column_name_and_attribute(self, teacher, aliased_attribute_schema):
        assert aliased_attribute_schema.fields["name"].attribute == "fname"
        dumped = unpack(aliased_attribute_schema.dump(teacher))
        assert dumped["name"] == teacher.fname


class TestModelInstanceDeserialization:
    @pytest.fixture
    def sqla_schema_class(self, models, session):
        class TeacherSchema(SQLAlchemySchema):
            class Meta:
                model = models.Teacher
                load_instance = True
                sqla_session = session
                strict = True  # marshmallow 2 compat

            full_name = auto_field(validate=validate.Length(max=20))
            current_school = auto_field()
            substitute = auto_field()

        return TeacherSchema

    @pytest.fixture
    def sqla_auto_schema_class(self, models, session):
        class TeacherSchema(SQLAlchemyAutoSchema):
            class Meta:
                model = models.Teacher
                include_relationships = True
                load_instance = True
                sqla_session = session
                strict = True  # marshmallow 2 compat

        return TeacherSchema

    @pytest.mark.parametrize(
        "SchemaClass",
        (
            pytest.lazy_fixture("sqla_schema_class"),
            pytest.lazy_fixture("sqla_auto_schema_class"),
        ),
    )
    def test_load(self, teacher, SchemaClass, models):
        schema_kwargs = (
            {"unknown": marshmallow.INCLUDE} if MARSHMALLOW_VERSION_INFO[0] >= 3 else {}
        )
        schema = SchemaClass(**schema_kwargs)
        dump_data = unpack(schema.dump(teacher))
        load_data = unpack(schema.load(dump_data))

        assert isinstance(load_data, models.Teacher)

    def test_load_transient(self, models, teacher):
        class TeacherSchema(SQLAlchemyAutoSchema):
            class Meta:
                model = models.Teacher
                load_instance = True
                transient = True
                strict = True  # marshmallow 2 compat

        schema = TeacherSchema()
        dump_data = unpack(schema.dump(teacher))
        load_data = unpack(schema.load(dump_data))
        assert isinstance(load_data, models.Teacher)
        state = sa.inspect(load_data)
        assert state.transient

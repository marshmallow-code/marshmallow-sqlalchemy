# -*- coding: utf-8 -*-
from __future__ import absolute_import
import datetime as dt
import decimal

import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref, column_property
from sqlalchemy.dialects import postgresql

from marshmallow import fields, validate, post_load

import pytest
from marshmallow_sqlalchemy import (
    fields_for_model, TableSchema, ModelSchema, ModelConverter, property2field, column2field,
    field_for, ModelConversionError
)
from marshmallow_sqlalchemy.fields import Related

def contains_validator(field, v_type):
    for v in field.validators:
        if isinstance(v, v_type):
            return v
    return False

class AnotherInteger(sa.Integer):
    """Use me to test if MRO works like we want"""
    pass

@pytest.fixture()
def Base():
    return declarative_base()


@pytest.fixture()
def engine():
    return sa.create_engine('sqlite:///:memory:', echo=False)


@pytest.fixture()
def session(Base, models, engine):
    engine = sa.create_engine('sqlite:///:memory:', echo=False)
    Session = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)
    return Session()


@pytest.fixture()
def models(Base):

    # models adapted from https://github.com/wtforms/wtforms-sqlalchemy/blob/master/tests/tests.py
    student_course = sa.Table(
        'student_course', Base.metadata,
        sa.Column('student_id', sa.Integer, sa.ForeignKey('student.id')),
        sa.Column('course_id', sa.Integer, sa.ForeignKey('course.id'))
    )

    class Course(Base):
        __tablename__ = 'course'
        id = sa.Column(sa.Integer, primary_key=True)
        name = sa.Column(sa.String(255), nullable=False)
        # These are for better model form testing
        cost = sa.Column(sa.Numeric(5, 2), nullable=False)
        description = sa.Column(sa.Text, nullable=False)
        level = sa.Column(sa.Enum('Primary', 'Secondary'))
        has_prereqs = sa.Column(sa.Boolean, nullable=False)
        started = sa.Column(sa.DateTime, nullable=False)
        grade = sa.Column(AnotherInteger, nullable=False)

        @property
        def url(self):
            return '/courses/{}'.format(self.id)

    class School(Base):
        __tablename__ = 'school'
        id = sa.Column(sa.Integer, primary_key=True)
        name = sa.Column(sa.String(255), nullable=False)

        @property
        def url(self):
            return '/schools/{}'.format(self.id)

    class Student(Base):
        __tablename__ = 'student'
        id = sa.Column(sa.Integer, primary_key=True)
        full_name = sa.Column(sa.String(255), nullable=False, unique=True, default='noname')
        dob = sa.Column(sa.Date(), nullable=True)
        date_created = sa.Column(sa.DateTime, default=dt.datetime.utcnow,
                doc='date the student was created')

        current_school_id = sa.Column(sa.Integer, sa.ForeignKey(School.id), nullable=False)
        current_school = relationship(School, backref=backref('students'))

        courses = relationship(
            'Course',
            secondary=student_course,
            backref=backref("students", lazy='dynamic')
        )

        @property
        def url(self):
            return '/students/{}'.format(self.id)

    class Teacher(Base):
        __tablename__ = 'teacher'
        id = sa.Column(sa.Integer, primary_key=True)

        full_name = sa.Column(sa.String(255), nullable=False, unique=True, default='Mr. Noname')

        current_school_id = sa.Column(sa.Integer, sa.ForeignKey(School.id), nullable=True)
        current_school = relationship(School, backref=backref('teachers'))

        substitute = relationship('SubstituteTeacher', uselist=False,
                                  backref='teacher')

    class SubstituteTeacher(Base):
        __tablename__ = 'substituteteacher'
        id = sa.Column(sa.Integer, sa.ForeignKey('teacher.id'),
                       primary_key=True)

    class Paper(Base):
        __tablename__ = 'paper'

        satype = sa.Column(sa.String(50))
        __mapper_args__ = {
            'polymorphic_identity': 'paper',
            'polymorphic_on': satype
        }

        id = sa.Column(sa.Integer, primary_key=True)
        name = sa.Column(sa.String, nullable=False, unique=True)

    class GradedPaper(Paper):
        __tablename__ = 'gradedpaper'

        __mapper_args__ = {
            'polymorphic_identity': 'gradedpaper'
        }

        id = sa.Column(sa.Integer, sa.ForeignKey('paper.id'),
                       primary_key=True)

        marks_available = sa.Column(sa.Integer)

    class Seminar(Base):
        __tablename__ = 'seminar'

        title = sa.Column(sa.String, primary_key=True)
        semester = sa.Column(sa.String, primary_key=True)

    class Lecture(Base):
        __tablename__ = 'lecture'
        __table_args__ = (
            sa.ForeignKeyConstraint(
                ['seminar_title', 'seminar_semester'],
                ['seminar.title', 'seminar.semester']
            ),
        )

        id = sa.Column(sa.Integer, primary_key=True)
        topic = sa.Column(sa.String)
        seminar_title = sa.Column(sa.String, sa.ForeignKey(Seminar.title))
        seminar_semester = sa.Column(sa.String, sa.ForeignKey(Seminar.semester))
        seminar = relationship(Seminar, foreign_keys=[seminar_title, seminar_semester])

    # So that we can access models with dot-notation, e.g. models.Course
    class _models(object):
        def __init__(self):
            self.Course = Course
            self.School = School
            self.Student = Student
            self.Teacher = Teacher
            self.SubstituteTeacher = SubstituteTeacher
            self.Paper = Paper
            self.GradedPaper = GradedPaper
            self.Seminar = Seminar
            self.Lecture = Lecture
    return _models()

@pytest.fixture()
def schemas(models, session):
    class CourseSchema(ModelSchema):
        class Meta:
            model = models.Course
            sqla_session = session

    class SchoolSchema(ModelSchema):
        class Meta:
            model = models.School
            sqla_session = session

    class StudentSchema(ModelSchema):
        class Meta:
            model = models.Student
            sqla_session = session

    class TeacherSchema(ModelSchema):
        class Meta:
            model = models.Teacher
            sqla_session = session

    class SubstituteTeacherSchema(ModelSchema):
        class Meta:
            model = models.SubstituteTeacher

    class PaperSchema(ModelSchema):
        class Meta:
            model = models.Paper
            sqla_session = session

    class GradedPaperSchema(ModelSchema):
        class Meta:
            model = models.GradedPaper
            sqla_session = session

    class HyperlinkStudentSchema(ModelSchema):
        class Meta:
            model = models.Student
            sqla_session = session

    class SeminarSchema(ModelSchema):
        class Meta:
            model = models.Seminar
            sqla_session = session

    class LectureSchema(ModelSchema):
        class Meta:
            model = models.Lecture
            sqla_session = session

    # Again, so we can use dot-notation
    class _schemas(object):
        def __init__(self):
            self.CourseSchema = CourseSchema
            self.SchoolSchema = SchoolSchema
            self.StudentSchema = StudentSchema
            self.TeacherSchema = TeacherSchema
            self.SubstituteTeacherSchema = SubstituteTeacherSchema
            self.PaperSchema = PaperSchema
            self.GradedPaperSchema = GradedPaperSchema
            self.HyperlinkStudentSchema = HyperlinkStudentSchema
            self.SeminarSchema = SeminarSchema
            self.LectureSchema = LectureSchema
    return _schemas()


class TestModelFieldConversion:

    def test_fields_for_model_types(self, models):
        fields_ = fields_for_model(models.Student, include_fk=True)
        assert type(fields_['id']) is fields.Int
        assert type(fields_['full_name']) is fields.Str
        assert type(fields_['dob']) is fields.Date
        assert type(fields_['current_school_id']) is fields.Int
        assert type(fields_['date_created']) is fields.DateTime

    def test_fields_for_model_handles_exclude(self, models):
        fields_ = fields_for_model(models.Student, exclude=('dob', ))
        assert type(fields_['id']) is fields.Int
        assert type(fields_['full_name']) is fields.Str
        assert 'dob' not in fields_

    def test_fields_for_model_handles_custom_types(self, models):
        fields_ = fields_for_model(models.Course, include_fk=True)
        assert type(fields_['grade']) is fields.Int

    def test_fields_for_model_saves_doc(self, models):
        fields_ = fields_for_model(models.Student, include_fk=True)
        assert fields_['date_created'].metadata['description'] == 'date the student was created'

    def test_length_validator_set(self, models):
        fields_ = fields_for_model(models.Student)
        validator = contains_validator(fields_['full_name'], validate.Length)
        assert validator
        assert validator.max == 255

    def test_sets_allow_none_for_nullable_fields(self, models):
        fields_ = fields_for_model(models.Student)
        assert fields_['dob'].allow_none is True

    def test_sets_enum_choices(self, models):
        fields_ = fields_for_model(models.Course)
        validator = contains_validator(fields_['level'], validate.OneOf)
        assert validator
        assert validator.choices == ('Primary', 'Secondary')

    def test_many_to_many_relationship(self, models):
        student_fields = fields_for_model(models.Student)
        assert type(student_fields['courses']) is fields.List

        course_fields = fields_for_model(models.Course)
        assert type(course_fields['students']) is fields.List

    def test_many_to_one_relationship(self, models):
        student_fields = fields_for_model(models.Student)
        assert type(student_fields['current_school']) is Related

        school_fields = fields_for_model(models.School)
        assert type(school_fields['students']) is fields.List

    def test_include_fk(self, models):
        student_fields = fields_for_model(models.Student, include_fk=False)
        assert 'current_school_id' not in student_fields

        student_fields2 = fields_for_model(models.Student, include_fk=True)
        assert 'current_school_id' in student_fields2

    def test_overridden_with_fk(self, models):
        graded_paper_fields = fields_for_model(models.GradedPaper,
                                               include_fk=False)
        assert 'id' in graded_paper_fields

def make_property(*column_args, **column_kwargs):
    return column_property(sa.Column(*column_args, **column_kwargs))

class TestPropertyFieldConversion:

    @pytest.fixture()
    def converter(self):
        return ModelConverter()

    def test_convert_String(self, converter):
        prop = make_property(sa.String())
        field = converter.property2field(prop)
        assert type(field) == fields.Str

    def test_convert_Unicode(self, converter):
        prop = make_property(sa.Unicode())
        field = converter.property2field(prop)
        assert type(field) == fields.Str

    def test_convert_Binary(self, converter):
        prop = make_property(sa.Binary())
        field = converter.property2field(prop)
        assert type(field) == fields.Str

    def test_convert_LargeBinary(self, converter):
        prop = make_property(sa.LargeBinary())
        field = converter.property2field(prop)
        assert type(field) == fields.Str

    def test_convert_Text(self, converter):
        prop = make_property(sa.types.Text())
        field = converter.property2field(prop)
        assert type(field) == fields.Str

    def test_convert_Date(self, converter):
        prop = make_property(sa.Date())
        field = converter.property2field(prop)
        assert type(field) == fields.Date

    def test_convert_DateTime(self, converter):
        prop = make_property(sa.DateTime())
        field = converter.property2field(prop)
        assert type(field) == fields.DateTime

    def test_convert_Boolean(self, converter):
        prop = make_property(sa.Boolean())
        field = converter.property2field(prop)
        assert type(field) == fields.Boolean

    def test_convert_Numeric(self, converter):
        prop = make_property(sa.Numeric(scale=2))
        field = converter.property2field(prop)
        assert type(field) == fields.Decimal
        assert field.places == decimal.Decimal((0, (1,), -2))

    def test_convert_Float(self, converter):
        prop = make_property(sa.Float(scale=2))
        field = converter.property2field(prop)
        assert type(field) == fields.Float

    def test_convert_SmallInteger(self, converter):
        prop = make_property(sa.SmallInteger())
        field = converter.property2field(prop)
        assert type(field) == fields.Int

    def test_convert_UUID(self, converter):
        prop = make_property(postgresql.UUID())
        field = converter.property2field(prop)
        assert type(field) == fields.UUID

    def test_convert_MACADDR(self, converter):
        prop = make_property(postgresql.MACADDR())
        field = converter.property2field(prop)
        assert type(field) == fields.Str

    def test_convert_INET(self, converter):
        prop = make_property(postgresql.INET())
        field = converter.property2field(prop)
        assert type(field) == fields.Str

    def test_convert_ARRAY_String(self, converter):
        prop = make_property(postgresql.ARRAY(sa.String()))
        field = converter.property2field(prop)
        assert type(field) == fields.List
        assert type(field.container) == fields.Str

    def test_convert_ARRAY_Integer(self, converter):
        prop = make_property(postgresql.ARRAY(sa.Integer))
        field = converter.property2field(prop)
        assert type(field) == fields.List
        assert type(field.container) == fields.Int

    def test_convert_TSVECTOR(self, converter):
        prop = make_property(postgresql.TSVECTOR)
        with pytest.raises(ModelConversionError):
            converter.property2field(prop)

class TestPropToFieldClass:

    def test_property2field(self):
        prop = make_property(sa.Integer())
        field = property2field(prop, instance=True)

        assert type(field) == fields.Int

        field_cls = property2field(prop, instance=False)
        assert field_cls == fields.Int

    def test_can_pass_extra_kwargs(self):
        prop = make_property(sa.String())
        field = property2field(prop, instance=True, description='just a string')
        assert field.metadata['description'] == 'just a string'

class TestColumnToFieldClass:

    def test_column2field(self):
        column = sa.Column(sa.String(255))
        field = column2field(column, instance=True)

        assert type(field) == fields.String

        field_cls = column2field(column, instance=False)
        assert field_cls == fields.String

    def test_can_pass_extra_kwargs(self):
        column = sa.Column(sa.String(255))
        field = column2field(column, instance=True, description='just a string')
        assert field.metadata['description'] == 'just a string'

class TestFieldFor:

    def test_field_for(self, models, session):
        field = field_for(models.Student, 'full_name')
        assert type(field) == fields.Str

        field = field_for(models.Student, 'current_school', session=session)
        assert type(field) == Related

class TestTableSchema:

    @pytest.fixture
    def school(self, models, session):
        table = models.School.__table__
        insert = table.insert().values(name='Univ. of Whales')
        with session.connection() as conn:
            conn.execute(insert)
            select = table.select().limit(1)
            return conn.execute(select).fetchone()

    def test_dump_row(self, models, school):
        class SchoolSchema(TableSchema):
            class Meta:
                table = models.School.__table__
        schema = SchoolSchema()
        dump = schema.dump(school).data
        assert dump == {'name': 'Univ. of Whales', 'id': 1}

class TestModelSchema:

    @pytest.fixture()
    def school(self, models, session):
        school_ = models.School(name='Univ. Of Whales')
        session.add(school_)
        session.flush()
        return school_

    @pytest.fixture()
    def student(self, models, school, session):
        student_ = models.Student(full_name='Monty Python', current_school=school)
        session.add(student_)
        session.flush()
        return student_

    @pytest.fixture()
    def teacher(self, models, school, session):
        teacher_ = models.Teacher(full_name='The Substitute Teacher')
        session.add(teacher_)
        session.flush()
        return teacher_

    @pytest.fixture()
    def subteacher(self, models, school, teacher, session):
        sub_ = models.SubstituteTeacher(teacher=teacher)
        session.add(sub_)
        session.flush()
        return sub_

    @pytest.fixture()
    def seminar(self, models, session):
        seminar_ = models.Seminar(title='physics', semester='spring')
        session.add(seminar_)
        session.flush()
        return seminar_

    @pytest.fixture()
    def lecture(self, models, session, seminar):
        lecture_ = models.Lecture(topic='force', seminar=seminar)
        session.add(lecture_)
        session.flush()
        return lecture_

    def test_model_schema_field_inheritance(self, schemas):
        class CourseSchemaSub(schemas.CourseSchema):
            additional = fields.Int()

        parent_schema = schemas.CourseSchema()
        child_schema = CourseSchemaSub()

        parent_schema_fields = set(parent_schema.declared_fields)
        child_schema_fields = set(child_schema.declared_fields)

        assert parent_schema_fields.issubset(child_schema_fields)
        assert 'additional' in child_schema_fields

    def test_model_schema_class_meta_inheritance(self, models, session):

        class BaseCourseSchema(ModelSchema):
            class Meta:
                model = models.Course
                sqla_session = session

        class CourseSchema(BaseCourseSchema):
            pass

        schema = CourseSchema()
        field_names = schema.declared_fields
        assert 'id' in field_names
        assert 'name' in field_names
        assert 'cost' in field_names

    def test_model_schema_dumping(self, schemas, student):
        schema = schemas.StudentSchema()
        result = schema.dump(student)
        # fk excluded by default
        assert 'current_school_id' not in result.data
        # related field dumps to pk
        assert result.data['current_school'] == student.current_school.id

    def test_model_schema_loading(self, models, schemas, student, session):
        schema = schemas.StudentSchema()
        dump_data = schema.dump(student).data
        result = schema.load(dump_data)

        assert result.data is student
        assert result.data.current_school == student.current_school

    def test_model_schema_loading_custom_instance(self, models, schemas, student, session):
        schema = schemas.StudentSchema(instance=student)
        dump_data = {'full_name': 'Terry Gilliam'}
        result = schema.load(dump_data)

        assert result.data is student
        assert result.data.current_school == student.current_school

    def test_model_schema_loading_no_instance_or_pk(self, models, schemas, student, session):
        schema = schemas.StudentSchema()
        dump_data = {'full_name': 'Terry Gilliam'}
        result = schema.load(dump_data)

        assert result.data is not student

    def test_model_schema_compound_key(self, schemas, seminar):
        schema = schemas.SeminarSchema()
        dump_data = schema.dump(seminar).data
        result = schema.load(dump_data)

        assert result.data is seminar

    def test_model_schema_compound_key_relationship(self, schemas, lecture):
        schema = schemas.LectureSchema()
        dump_data = schema.dump(lecture).data
        assert dump_data['seminar'] == {
            'title': lecture.seminar_title,
            'semester': lecture.seminar_semester,
        }
        result = schema.load(dump_data)

        assert result.data is lecture

    def test_model_schema_compound_key_relationship_invalid_key(self, schemas, lecture):
        schema = schemas.LectureSchema()
        dump_data = schema.dump(lecture).data
        dump_data['seminar'] = 'scalar'
        with pytest.raises(ValueError):
            schema.load(dump_data)

    def test_model_schema_loading_passing_session_to_load(self, models, schemas, student, session):
        class StudentSchemaNoSession(ModelSchema):
            class Meta:
                model = models.Student

        schema = StudentSchemaNoSession()
        dump_data = schema.dump(student).data
        result = schema.load(dump_data, session=session)
        assert type(result.data) == models.Student
        assert result.data.current_school == student.current_school

    def test_model_schema_validation_passing_session_to_validate(self, models,
            schemas, student, session):
        class StudentSchemaNoSession(ModelSchema):
            class Meta:
                model = models.Student

        schema = StudentSchemaNoSession()
        dump_data = schema.dump(student).data
        assert type(schema.validate(dump_data, session=session)) is dict

    def test_model_schema_loading_passing_session_to_constructor(self,
            models, schemas, student, session):
        class StudentSchemaNoSession(ModelSchema):
            class Meta:
                model = models.Student

        schema = StudentSchemaNoSession(session=session)
        dump_data = schema.dump(student).data
        result = schema.load(dump_data)
        assert type(result.data) == models.Student
        assert result.data.current_school == student.current_school

    def test_model_schema_validation_passing_session_to_constructor(self,
            models, schemas, student, session):
        class StudentSchemaNoSession(ModelSchema):
            class Meta:
                model = models.Student

        schema = StudentSchemaNoSession(session=session)
        dump_data = schema.dump(student).data
        assert type(schema.validate(dump_data)) is dict

    def test_model_schema_loading_and_validation_with_no_session_raises_error(self,
            models, schemas, student, session):
        class StudentSchemaNoSession(ModelSchema):
            class Meta:
                model = models.Student

        schema = StudentSchemaNoSession()
        dump_data = schema.dump(student).data
        with pytest.raises(ValueError) as excinfo:
            schema.load(dump_data)
        assert excinfo.value.args[0] == 'Deserialization requires a session'

        with pytest.raises(ValueError) as excinfo:
            schema.validate(dump_data)
        assert excinfo.value.args[0] == 'Validation requires a session'

    def test_model_schema_custom_related_column(self, models, schemas, student, session):
        class StudentSchema(ModelSchema):
            class Meta:
                model = models.Student
                sqla_session = session
            current_school = Related(column='name')

        schema = StudentSchema()
        dump_data = schema.dump(student).data
        result = schema.load(dump_data)

        assert type(result.data) == models.Student
        assert result.data.current_school == student.current_school

    def test_dump_many_to_one_relationship(self, models, schemas, school, student):
        schema = schemas.SchoolSchema()
        dump_data = schema.dump(school).data

        assert dump_data['students'] == [student.id]

    def test_load_many_to_one_relationship(self, models, schemas, school, student):
        schema = schemas.SchoolSchema()
        load_data = schema.load({'students': [1]}).data
        assert type(load_data.students[0]) is models.Student
        assert load_data.students[0] == student

    def test_fields_option(self, student, models, session):
        class StudentSchema(ModelSchema):
            class Meta:
                model = models.Student
                sqla_session = session
                fields = ('full_name', 'date_created')

        session.commit()
        schema = StudentSchema()
        data, errors = schema.dump(student)

        assert 'full_name' in data
        assert 'date_created' in data
        assert 'dob' not in data
        assert len(data.keys()) == 2

    def test_exclude_option(self, student, models, session):
        class StudentSchema(ModelSchema):
            class Meta:
                model = models.Student
                sqla_session = session
                exclude = ('date_created', )

        session.commit()
        schema = StudentSchema()
        data, errors = schema.dump(student)

        assert 'full_name' in data
        assert 'date_created' not in data

    def test_additional_option(self, student, models, session):
        class StudentSchema(ModelSchema):
            uppername = fields.Function(lambda x: x.full_name.upper())

            class Meta:
                model = models.Student
                sqla_session = session
                additional = ('date_created', )

        session.commit()
        schema = StudentSchema()
        data, errors = schema.dump(student)
        assert 'full_name' in data
        assert 'uppername' in data
        assert data['uppername'] == student.full_name.upper()

    def test_field_override(self, student, models, session):
        class MyString(fields.Str):
            def _serialize(self, val, attr, obj):
                return val.upper()

        class StudentSchema(ModelSchema):
            full_name = MyString()

            class Meta:
                model = models.Student
                sqla_session = session

        session.commit()
        schema = StudentSchema()
        data, errors = schema.dump(student)
        assert 'full_name' in data
        assert data['full_name'] == student.full_name.upper()

    def test_a_teacher_who_is_a_substitute(self, models, schemas, teacher,
                                           subteacher, session):
        session.commit()
        schema = schemas.TeacherSchema()
        data, errors = schema.dump(teacher)
        result = schema.load(data)

        assert not result.errors
        assert type(result.data) is models.Teacher
        assert 'substitute' in data
        assert data['substitute'] == subteacher.id

    def test_dump_only_relationship(self, models, session, school, student):
        class SchoolSchema2(ModelSchema):
            class Meta:
                model = models.School
            students = field_for(models.School, 'students', dump_only=True)

            # override for easier testing
            @post_load
            def make_instance(self, data):
                return data

        sch = SchoolSchema2()
        students_field = sch.fields['students']

        assert students_field.dump_only is True
        dump_data = sch.dump(school).data
        result = sch.load(dump_data, session=session)
        assert 'students' not in result.data

class TestNullForeignKey:
    @pytest.fixture()
    def school(self, models, session):
        school_ = models.School(name='The Teacherless School')
        session.add(school_)
        session.flush()
        return school_

    @pytest.fixture()
    def teacher(self, models, school, session):
        teacher_ = models.Teacher(full_name='The Schoolless Teacher')
        session.add(teacher_)
        session.flush()
        return teacher_

    def test_a_teacher_with_no_school(self, models, schemas, teacher, session):
        session.commit()
        schema = schemas.TeacherSchema()
        dump_data = schema.dump(teacher).data
        result = schema.load(dump_data)

        assert type(result.data) == models.Teacher
        assert result.data.current_school is None

    def test_a_teacher_who_is_not_a_substitute(self, models, schemas, teacher,
                                               session):
        session.commit()
        schema = schemas.TeacherSchema()
        data, errors = schema.dump(teacher)
        result = schema.load(data)

        assert not result.errors

        assert type(result.data) is models.Teacher
        assert 'substitute' in data
        assert data['substitute'] == None

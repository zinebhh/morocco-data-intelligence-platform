import pytest
from pydantic import ValidationError

from data_engineering.common.schemas.university_schema import UniversitySchema
from data_engineering.common.schemas.faculty_schema import FacultySchema
from data_engineering.common.schemas.program_schema import ProgramSchema


def test_valid_university():

    university = UniversitySchema(
        source_id="UH2-CASA",
        name="Université Hassan II",
        type="Public",
        city="Casablanca",
        region="Casablanca-Settat",
        source="test",
    )

    assert university.name == "Université Hassan II"


def test_invalid_university():

    with pytest.raises(ValidationError):

        UniversitySchema(
            source_id="",
            name="",
            type="",
            city="",
            source="",
        )


def test_valid_faculty():

    faculty = FacultySchema(
        source_id="FSAC",
        university_source_id="UH2-CASA",
        name="Faculté des Sciences Ain Chock",
        city="Casablanca",
        source="test",
    )

    assert faculty.name == "Faculté des Sciences Ain Chock"


def test_valid_program():

    program = ProgramSchema(
        source_id="BD2C",
        faculty_source_id="FSAC",
        name="Big Data et Cloud Computing",
        degree_level="Master",
        source="test",
    )

    assert program.degree_level == "Master"
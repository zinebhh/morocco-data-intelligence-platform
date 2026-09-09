"""
Validation example for UniversitySchema.
"""

from pydantic import ValidationError

from data_engineering.common.schemas.university_schema import UniversitySchema


def validate_university():
    """Validate a sample university."""

    university_data = {
        "source_id": "UH2-CASA",
        "name": "Université Hassan II",
        "name_ar": "جامعة الحسن الثاني",
        "type": "Public",
        "city": "Casablanca",
        "region": "Casablanca-Settat",
        "website": "https://www.univh2c.ma/",
        "status": "active",
        "source": "university_website",
        "source_url": "https://www.univh2c.ma/",
    }

    try:
        university = UniversitySchema(**university_data)

        print("VALID UNIVERSITY")
        print(university.model_dump())

        return university

    except ValidationError as error:
        print("INVALID UNIVERSITY")
        print(error)

        return None


if __name__ == "__main__":
    validate_university()
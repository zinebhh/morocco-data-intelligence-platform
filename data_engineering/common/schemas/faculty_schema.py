from typing import Optional

from pydantic import BaseModel, Field


class FacultySchema(BaseModel):

    source_id: str = Field(min_length=2)

    university_source_id: str = Field(min_length=2)

    name: str = Field(min_length=2)

    city: Optional[str] = None

    source: str = Field(min_length=2)
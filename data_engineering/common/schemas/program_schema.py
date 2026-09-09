from typing import Optional

from pydantic import BaseModel, Field


class ProgramSchema(BaseModel):

    source_id: str = Field(min_length=2)

    faculty_source_id: str = Field(min_length=2)

    name: str = Field(min_length=2)

    degree_level: Optional[str] = None

    field: Optional[str] = None

    source: str = Field(min_length=2)
"""
Data contract for Moroccan universities.
"""

from typing import Optional

from pydantic import BaseModel, Field, HttpUrl


class UniversitySchema(BaseModel):
    """Canonical schema for a Moroccan university."""

    source_id: str = Field(
        min_length=2,
        description="Identifier of the university in the source system",
    )

    name: str = Field(
        min_length=2,
        description="University name",
    )

    name_ar: Optional[str] = None

    type: str = Field(
        min_length=2,
        description="University type",
    )

    city: str = Field(
        min_length=2,
        description="University city",
    )

    region: Optional[str] = None

    website: Optional[HttpUrl] = None

    status: str = Field(
        default="active",
        description="University status",
    )

    source: str = Field(
        min_length=2,
        description="Data source",
    )

    source_url: Optional[HttpUrl] = None
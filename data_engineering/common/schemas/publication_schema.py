"""
Data contract for scientific publications.
"""

from typing import Optional

from pydantic import BaseModel, Field, HttpUrl


class PublicationSchema(BaseModel):
    """Canonical schema for a scientific publication."""

    source_id: Optional[str] = None

    title: str = Field(
        min_length=2,
        description="Publication title",
    )

    abstract: Optional[str] = None

    publication_year: Optional[int] = Field(
        default=None,
        ge=1900,
        le=2100,
    )

    publication_date: Optional[str] = None

    doi: Optional[str] = None

    journal: Optional[str] = None

    publisher: Optional[str] = None

    research_field: Optional[str] = None

    citation_count: int = Field(
        default=0,
        ge=0,
    )

    authors: list[str] = Field(default_factory=list)

    institutions: list[str] = Field(default_factory=list)

    keywords: list[str] = Field(default_factory=list)

    source: str = Field(
        min_length=2,
        description="Data source",
    )

    source_url: Optional[HttpUrl] = None
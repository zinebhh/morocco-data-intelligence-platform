import logging
from typing import Any

from data_engineering.common.schemas.publication_schema import (
    PublicationSchema,
)

logger = logging.getLogger(__name__)


def map_openalex_work(
    work: dict[str, Any],
) -> PublicationSchema:
    """
    Convert an OpenAlex work into the platform's
    canonical PublicationSchema.
    """

    primary_location = (
        work.get("primary_location")
        or {}
    )

    source_info = (
        primary_location.get("source")
        or {}
    )

    # -----------------------------
    # Research field
    # -----------------------------

    topics = work.get("topics") or []

    research_field = None

    if topics:
        first_topic = topics[0] or {}

        research_field = (
            first_topic.get("display_name")
        )

    # -----------------------------
    # Authors and institutions
    # -----------------------------

    authors = []

    institutions = []

    authorships = (
        work.get("authorships")
        or []
    )

    for authorship in authorships:

        author = (
            authorship.get("author")
            or {}
        )

        author_name = (
            author.get("display_name")
        )

        if author_name:
            authors.append(author_name)

        for institution in (
            authorship.get("institutions")
            or []
        ):

            institution_name = (
                institution.get("display_name")
            )

            if institution_name:
                institutions.append(
                    institution_name
                )

    # Remove duplicates
    authors = list(
        dict.fromkeys(authors)
    )

    institutions = list(
        dict.fromkeys(institutions)
    )

    # -----------------------------
    # Keywords
    # -----------------------------

    keywords = []

    for keyword in (
        work.get("keywords")
        or []
    ):

        keyword_name = (
            keyword.get("display_name")
        )

        if keyword_name:
            keywords.append(keyword_name)

    # -----------------------------
    # Create canonical publication
    # -----------------------------

    return PublicationSchema(

        source_id=work.get("id"),

        title=(
            work.get("display_name")
            or ""
        ).strip(),

        abstract=None,

        publication_year=(
            work.get("publication_year")
        ),

        publication_date=(
            work.get("publication_date")
        ),

        doi=work.get("doi"),

        journal=(
            source_info.get("display_name")
        ),

        publisher=(
            source_info.get("host_organization_name")
        ),

        research_field=research_field,

        citation_count=(
            work.get("cited_by_count")
            or 0
        ),

        authors=authors,

        institutions=institutions,

        keywords=keywords,

        source="openalex",

        source_url=(
            work.get("id")
        ),
    )
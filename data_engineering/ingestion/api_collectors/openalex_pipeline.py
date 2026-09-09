"""
OpenAlex ingestion pipeline.

Pipeline:

OpenAlex API
    ->
Raw JSON
    ->
Mapping
    ->
Validation
    ->
Processed JSON
"""

import json
import logging

from datetime import datetime
from pathlib import Path
from typing import Any


from data_engineering.ingestion.api_collectors.openalex_collector import (
    OpenAlexCollector,
)

from data_engineering.ingestion.api_collectors.openalex_mapper import (
    map_openalex_work,
)


logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(message)s"
    ),
)

logger = logging.getLogger(__name__)


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[3]
)


RAW_DIR = (
    PROJECT_ROOT
    / "data_engineering"
    / "ingestion"
    / "raw"
)


PROCESSED_DIR = (
    PROJECT_ROOT
    / "data_engineering"
    / "ingestion"
    / "processed"
)


ERRORS_DIR = (
    PROJECT_ROOT
    / "data_engineering"
    / "ingestion"
    / "errors"
)


def save_json(
    data: Any,
    file_path: Path,
) -> None:

    """
    Save data as UTF-8 JSON.
    """

    file_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        file_path,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=2,
            default=str,
        )

    logger.info(
        "Saved file: %s",
        file_path,
    )


def run_pipeline(
    search_query: str = (
        "Morocco university"
    ),
    per_page: int = 20,
) -> list[dict[str, Any]]:

    logger.info(
        "=" * 60
    )

    logger.info(
        "STARTING OPENALEX PIPELINE"
    )

    logger.info(
        "=" * 60
    )


    # --------------------------------
    # 1. COLLECT RAW DATA
    # --------------------------------

    logger.info(
        "STEP 1 - Collecting data"
    )

    collector = (
        OpenAlexCollector()
    )

    raw_works = (
        collector.search_works(
            search=search_query,
            per_page=per_page,
        )
    )

    logger.info(
        "Collected %s raw works",
        len(raw_works),
    )


    # --------------------------------
    # 2. SAVE RAW DATA
    # --------------------------------

    timestamp = (
        datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )
    )

    raw_file = (
        RAW_DIR
        / f"openalex_raw_{timestamp}.json"
    )

    save_json(
        raw_works,
        raw_file,
    )


    # --------------------------------
    # 3. MAP AND VALIDATE
    # --------------------------------

    logger.info(
        "STEP 2 - Mapping and validating"
    )

    processed_works = []

    errors = []


    for work in raw_works:

        try:

            publication = (
                map_openalex_work(
                    work
                )
            )

            processed_works.append(
                publication.model_dump(
                    mode="json"
                )
            )

        except Exception as error:

            logger.warning(
                "Mapping failed: %s",
                error,
            )

            errors.append(
                {
                    "work_id":
                        work.get("id"),

                    "title":
                        work.get(
                            "display_name"
                        ),

                    "error":
                        str(error),
                }
            )


    # --------------------------------
    # 4. SAVE PROCESSED DATA
    # --------------------------------

    processed_file = (
        PROCESSED_DIR
        / (
            f"openalex_processed_"
            f"{timestamp}.json"
        )
    )

    save_json(
        processed_works,
        processed_file,
    )


    # --------------------------------
    # 5. SAVE ERRORS
    # --------------------------------

    if errors:

        errors_file = (
            ERRORS_DIR
            / (
                f"openalex_errors_"
                f"{timestamp}.json"
            )
        )

        save_json(
            errors,
            errors_file,
        )


    # --------------------------------
    # SUMMARY
    # --------------------------------

    logger.info(
        "=" * 60
    )

    logger.info(
        "PIPELINE COMPLETED"
    )

    logger.info(
        "Raw records: %s",
        len(raw_works),
    )

    logger.info(
        "Processed records: %s",
        len(processed_works),
    )

    logger.info(
        "Errors: %s",
        len(errors),
    )

    logger.info(
        "=" * 60
    )


    return processed_works


if __name__ == "__main__":

    results = run_pipeline(
        search_query=(
            "Morocco university"
        ),
        per_page=20,
    )

    print(
        f"\nPipeline completed: "
        f"{len(results)} "
        f"publications processed"
    )
import logging

import requests

from typing import Any


logger = logging.getLogger(__name__)


class OpenAlexCollector:

    BASE_URL = (
        "https://api.openalex.org/works"
    )

    def __init__(
        self,
        timeout: int = 30,
    ):

        self.timeout = timeout

        self.session = requests.Session()

        self.session.headers.update(
            {
                "User-Agent":
                    "Morocco Data Intelligence Platform/1.0"
            }
        )


    def search_works(
        self,
        search: str,
        per_page: int = 10,
    ) -> list[dict[str, Any]]:

        params = {
            "search": search,
            "per-page": per_page,
        }

        logger.info(
            "Searching OpenAlex: "
            "search=%s per_page=%s",
            search,
            per_page,
        )

        response = self.session.get(
            self.BASE_URL,
            params=params,
            timeout=self.timeout,
        )

        response.raise_for_status()

        data = response.json()

        results = (
            data.get("results")
            or []
        )

        logger.info(
            "OpenAlex returned %s works",
            len(results),
        )

        return results
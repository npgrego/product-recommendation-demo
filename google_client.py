from typing import Any
from serpapi import Client
import copy
import logging

from schemas import (
    GoogleShoppingProductsResponse, 
    GoogleShoppingProductResponse
)
from config import app_settings

logger = logging.getLogger(__name__)


LOCATION_2_GOOGLE_PARAMS = {
    "us": {
        "google_domain": "google.com",
        "gl": "us",
        "hl": "en",
        "location": "East Hanover, New Jersey, United States",
    },
    "pl": {
        "google_domain": "google.pl",
        "gl": "pl",
        "hl": "pl",
        "location": "Lesser Poland Voivodeship, Poland",
    },
    "de": {
        "google_domain": "google.de",
        "gl": "de",
        "hl": "de",
        "location": "Berlin",
    },
    "es": {
        "google_domain": "google.es",
        "gl": "es",
        "hl": "es",
        "location": "Community of Madrid,Spain",
    },
    "gb": {
        "google_domain": "google.co.uk",
        "gl": "uk",
        "hl": "en",
        "location": "London, England, United Kingdom",
    },
}

class GoogleClient:

    def __init__(self) -> None:
        self.client = Client(api_key=app_settings.serp_api_key)

    def _search_by_location(self, engine: str, location: str, **kwargs) -> dict[str, Any]:

        params = copy.copy(LOCATION_2_GOOGLE_PARAMS[location])
        params["engine"] = engine
        params.update(kwargs)

        logger.info(f"Calling to SERP {engine} API for {location} location")

        response = self.client.search(**params).as_dict()
        return response

    def get_products(self, query: str, location: str) -> GoogleShoppingProductsResponse:
        logger.info("Calling to SERP Shopping API")
        return GoogleShoppingProductsResponse(
            **self._search_by_location(engine="google_shopping", location=location, q=query)
        )

        # products = response.shopping_results 
        # # + response.related_shopping_results
        # # TODO Dedupe

        # logger.info(f"Got {len(products)} prodcuts from SERP shopping API")
        # if app_settings.max_candidates:
        #     logger.info(f"Reducing candidates to max {app_settings.max_candidates}")
        #     products = products[:app_settings.max_candidates]

        # return products

    def get_product(self, product_id: str, location: str) -> GoogleShoppingProductResponse:
        logger.info("Calling to SERP Shopping Product API")
        return GoogleShoppingProductResponse(
            **self._search_by_location(engine="google_product", location=location, product_id=product_id)
        )

        # return response.sellers_results.online_sellers



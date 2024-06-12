from typing import Any
from serpapi import Client
import copy
import logging

from schemas import GoogleShoppingResponse, GoogleShoppingProduct, GoogleShoppingProductResponse
from config import app_settings

logger = logging.getLogger(__name__)


LOCATION_2_GOOGLE_PARAMS = {
    "us": {
        "engine": "google_shopping",
        "google_domain": "google.com",
        "gl": "us",
        "hl": "en",
        "location": "United States",
    },
    "pl": {
        "engine": "google_shopping",
        "google_domain": "google.pl",
        "gl": "pl",
        "hl": "pl",
        "location": "Warsaw",
    },
    "de": {
        "engine": "google_shopping",
        "google_domain": "google.de",
        "gl": "de",
        "hl": "de",
        "location": "Berlin",
    },
    "es": {
        "engine": "google_shopping",
        "google_domain": "google.es",
        "gl": "es",
        "hl": "es",
        "location": "Community of Madrid,Spain",
    },
    "gb": {
        "engine": "google_shopping",
        "google_domain": "google.co.uk",
        "gl": "uk",
        "hl": "en",
        "location": "East Hanover, New Jersey, United States",
    },
}

class GoogleShoppingClient:
    def __init__(self) -> None:
        self.client = Client(api_key=app_settings.serp_api_key)

    def get_response(self, query: str, location: str) -> dict[str, Any]:

        params = copy.copy(LOCATION_2_GOOGLE_PARAMS[location])
        params["q"] = query

        logger.info(f"Calling to SERP shopping API for {location} location")

        response = self.client.search(**params).as_dict()
        return response
        
    
    def parse_response(self, response: dict[str, Any]) -> list[GoogleShoppingProduct]:
        shopping_search_result = GoogleShoppingResponse(**response)

        candidates = shopping_search_result.shopping_results + shopping_search_result.related_shopping_results

        logger.info(f"Got {len(candidates)} from SERP shopping API, reducing to max {app_settings.max_candidates}")
        if app_settings.max_candidates:
            logger.info(f"Reducing candidates to max {app_settings.max_candidates}")
            candidates = candidates[:app_settings.max_candidates]

        return candidates

    def get_candidates(self, query: str, location: str) -> list[GoogleShoppingProduct]:
        return self.parse_response(
            self.get_response(query=query, location=location)
        )
    
    def get_comparisons(self, params: str) -> list[GoogleShoppingProduct]:
        logger.info("Calling to SERP Shopping Product API")
        response = self.client.search(**params).as_dict()
        offers = GoogleShoppingProductResponse(**response)

        return offers.sellers_results.online_sellers



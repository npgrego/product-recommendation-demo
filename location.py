from typing import Any
import requests
import streamlit as st
from datetime import date
from pydantic import BaseModel

CURRENCY_UAH = "UAH"
CURRENCY_EUR = "EUR"
CURRENCY_USD = "USD"
CURRENCY_PLN = "PLN"
CURRENCY_GBP = "GBP"

DESCRIPTION_LOCATION = {
    "🇺🇸 United States": "us",
    "🇵🇱 Warsaw, Poland": "pl",
    "🇩🇪 Berlin, Germany": "de",
    "🇪🇸 Madrid, Spain": "es",
    "🇬🇧 London, UK": "gb"
}

LOCATION_DESCRIPTION = {v:k for k,v in DESCRIPTION_LOCATION.items()}

LOCATION_DEFAULT_CURRENCY = {
    "us": "USD",
    "pl": "PLN",
    "de": "EUR",
    "es": "EUR",
    "gb": "GBP"
}

CODE_CURRENCY = {
    978: CURRENCY_EUR,
    840: CURRENCY_USD,
    985: CURRENCY_PLN,
    826: CURRENCY_GBP
}

CURRENCY_CODE_UAH = 980

REPR_CURRENCY = {
    "zł": "PLN",
    "zl": "PLN",
    "грн": "UAH",
    "₴": "UAH",
    "€": "EUR",
    "$": "USD",
    "£": "GBP",
    "us": "USD",
    "dollar": "USD",
    "dollars": "USD"
}


class MonoExchangeRate(BaseModel):
    currencyCodeA: int
    currencyCodeB: int
    rateBuy: float | None = None
    rateSell: float | None = None
    rateCross: float | None = None


@st.cache_data
def get_exchange_rates(date: date) -> dict[str, float]:
    print("Connecting to Monobank")

    r = requests.get("https://api.monobank.ua/bank/currency")

    r.raise_for_status()

    mono_rates: list[dict[str, Any]] = r.json()
    exchange_rates = {}

    for mono_rate_data in mono_rates:
        mono_rate = MonoExchangeRate(**mono_rate_data)

        if mono_rate.currencyCodeB != CURRENCY_CODE_UAH:
            continue

        if mono_rate.currencyCodeA not in CODE_CURRENCY:
            continue

        exchange_rates[CODE_CURRENCY[mono_rate.currencyCodeA]] = mono_rate.rateSell or mono_rate.rateCross

    return exchange_rates

def get_price_currency(price: str, location:str) -> str:
    currency = None

    for repr, cur in REPR_CURRENCY.items():
        if repr in price:
            currency = cur
            break

    if not currency:
        currency = LOCATION_DEFAULT_CURRENCY[location]

    return currency
import requests
from requests.auth import HTTPBasicAuth
from urllib.parse import urljoin

from config import app_settings
import streamlit as st
from pydantic import BaseModel, Field

class CandidateProduct(BaseModel):
    title: str
    position: int | None = Field(..., description="Some desctiption", title="and title")
    link: str | None = None
    thumbnail: str | None = None
    extracted_price: float | None = None
    price: str | None = None
    rating: float | None = None
    store_rating: float | None = None
    similarity: float = 0

class RecommendProductsResponse(BaseModel):
    products: list[CandidateProduct]

class RecommendProductsByLocationRequest(BaseModel):
    product_url: str
    location: str

def show_candidate_list(candidates: list[CandidateProduct], show_similarity=False) -> None:
    for c in candidates:
        col_image, col_title, col_link, col_price = st.columns(4)
        col_image.image(c.thumbnail)
        col_title.write(
            f"{c.title}, similarity: {round(c.similarity*100, 1)} %" if c.similarity and show_similarity else c.title
        )
        col_link.markdown(f"[link]({c.link})")
        col_price.write(f"{c.price} ({c.extracted_price})")

def get_candidates(product_url, location):

    payload = RecommendProductsByLocationRequest(
        product_url=product_url,
        location=location
    )

    response = requests.post(
        url=urljoin(app_settings.app_server, "/recommend-products-location/"), 
        auth=HTTPBasicAuth(app_settings.app_username, app_settings.app_password),
        json=payload.model_dump()
    )
    response.raise_for_status()
    
    return RecommendProductsResponse(**response.json()).products

def show():
    
    st.header("Nova Product Search")

    product_url = st.text_input("Product URL")
    location = st.selectbox("Location", options=("us", "pl", "de", "es", "gb"))

    if st.button("Search", disabled=not bool(product_url)):
        candidates = get_candidates(product_url=product_url, location=location)
        show_candidate_list(candidates=candidates)


if __name__ == "__main__":
    show()
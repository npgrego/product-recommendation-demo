from typing import Tuple
import requests
from requests.auth import HTTPBasicAuth
from urllib.parse import urljoin
import streamlit as st
from datetime import date

from config import app_settings
from schemas import CandidateProduct, RequestedProduct, RecommendProductsRequest, GenerateCandidatesRequest, RecommendProductsResponse, PreparedCandidateProduct
from location import LOCATION_DESCRIPTION, get_exchange_rates, get_price_currency


def show_prepared_candidates(
        filter_min_similarity:int|None=None,
        filter_max_price:float|None=None, 
        sort_by:str|None=None, 
        show_similarity:bool=False
    ) -> None:
    prepared_candidates:list[PreparedCandidateProduct] = st.session_state["prepared_candidates"]
    used_prepared_candidates:list[PreparedCandidateProduct] = []

    for c in prepared_candidates:
        if filter_min_similarity and c.similarity*100<filter_min_similarity:
            continue

        if filter_max_price and c.price_uah>filter_max_price:
            continue

        used_prepared_candidates.append(c)

    min_price, max_price = get_min_max_price(used_prepared_candidates)

    st.write(f"## Shown {len(used_prepared_candidates)} out of {len(prepared_candidates)}, price range {min_price}-{max_price} UAH")

    if sort_by=="price":
        used_prepared_candidates = sorted(used_prepared_candidates, key=lambda c: c.price_uah)
    else:
        used_prepared_candidates = sorted(used_prepared_candidates, key=lambda c: c.similarity, reverse=True)

    for c in used_prepared_candidates:

        loc_desc = LOCATION_DESCRIPTION[c.location].split()[0]
        col_image, col_title, col_link, col_price_uah, col_price = st.columns(5)
        col_image.image(c.thumbnail)
        col_title.write(
            f"{loc_desc} {c.title}, similarity: {round(c.similarity*100, 1)} %" if c.similarity and show_similarity else c.title
        )
        col_link.markdown(f"[link]({c.link})")
        col_price_uah.write(f"{c.price_uah} UAH")
        col_price.write(f"{c.extracted_price} {c.currency}")
        

def parse_product(product_url):

    payload = RecommendProductsRequest(
        product_url=product_url
    )

    response = requests.post(
        url=urljoin(app_settings.app_server, "/parse-product/"), 
        auth=HTTPBasicAuth(app_settings.app_username, app_settings.app_password),
        json=payload.model_dump()
    )
    response.raise_for_status()
    
    return RequestedProduct(**response.json())

def generate_candidates(query, main_image, location):

    payload = GenerateCandidatesRequest(
        query=query,
        main_image=main_image,
        location=location
    )

    response = requests.post(
        url=urljoin(app_settings.app_server, "/generate-candidates/"), 
        auth=HTTPBasicAuth(app_settings.app_username, app_settings.app_password),
        json=payload.model_dump()
    )
    response.raise_for_status()
    
    return RecommendProductsResponse(**response.json()).products


def prepare_candidates(candidates: list[CandidateProduct], location:str) -> list[PreparedCandidateProduct]:
    exchange_rates: dict[str, float] = st.session_state["exchange_rates"]
    
    prepared_candidates = []
    for candidate in candidates:
        currency=get_price_currency(price=candidate.price, location=location)
        rate = exchange_rates[currency]

        prepared_candidate = PreparedCandidateProduct(
            **candidate.model_dump(),
            currency=currency,
            price_uah=round(candidate.extracted_price*rate),
            location=location
        )
        prepared_candidates.append(prepared_candidate)
    
    return prepared_candidates

def get_min_max_price(prepared_candidates:list[PreparedCandidateProduct])-> Tuple[int,int]:

    if not prepared_candidates:
        return 0,0

    min_price = max_price = prepared_candidates[0].price_uah
    for c in prepared_candidates:
        if c.price_uah> max_price:
            max_price = c.price_uah
        if c.price_uah<min_price:
            min_price = c.price_uah

    return min_price, max_price


def show():
    
    st.header("Nova Product Search")

    if "exchange_rates" not in st.session_state:
        st.session_state["exchange_rates"] = get_exchange_rates(date.today())
    
    if "prepared_candidates" not in st.session_state:
        st.session_state["prepared_candidates"] = []

    if "request_product" not in st.session_state:
        st.session_state["request_product"] = None

    product_url = st.text_input("Product URL")

    if st.button("Parse product", disabled=not product_url):
        try:
            st.session_state["request_product"] = parse_product(product_url=product_url)
        except Exception as e:
            st.error(e)
            st.session_state["request_product"] = None


    requested_product = st.session_state["request_product"]
    if requested_product:
        with st.expander("Parsed info"):
            st.image(requested_product.main_image, width=400)
            st.write(requested_product.title)
            st.write(requested_product.description)
            st.write(requested_product.price)
            st.write(requested_product.currency)
            st.write(requested_product.query)

    st.divider()

    query = st.text_input("Google Query")
    main_image = st.text_input("Main image Url")

    location_cols = st.columns(len(LOCATION_DESCRIPTION))

    for idx, location_description in enumerate(LOCATION_DESCRIPTION.items()):
        location, description = location_description
        location_cols[idx].checkbox(label=description, key=f"_location_{location}")
    
    selected_locations = []

    for location in LOCATION_DESCRIPTION:
        if st.session_state[f"_location_{location}"]:
            selected_locations.append(location)


    if st.button("Generate candidates", disabled=not len(selected_locations) or not query):
        prepared_candidates = []
        with st.status(f"Generating candidates from {len(selected_locations)} location(s)", expanded=True) as status:
            
            for location in selected_locations:
                st.write(f"Generating candidates for {location}...")
                try:
                    location_candidates = generate_candidates(
                        query=query,
                        main_image=main_image, 
                        location=location
                    )
                    st.write(f"Preparing candidates for {location}...")
                    prepared_candidates+=prepare_candidates(
                        candidates=location_candidates, 
                        location=location
                    )
                except Exception as e:
                    st.error(e)
                
            status.update(label="Candidate generation complete!", state="complete", expanded=False)
        
        st.session_state["prepared_candidates"] = prepared_candidates


    if st.session_state["prepared_candidates"]:

        min_price, max_price = get_min_max_price(st.session_state["prepared_candidates"])
        
        filter_min_similarity = st.slider("Min Similarity", min_value=0, max_value=100, value=0, step=1)
        filter_max_price = st.slider("Min price", min_value=min_price, max_value=min_price, value=max_price, step=1)
        sort_by = st.radio("Sort by", options=["price", "similarity"], horizontal=True)

        show_prepared_candidates(
            show_similarity=True,
            filter_min_similarity=filter_min_similarity,
            filter_max_price=filter_max_price, 
            sort_by=sort_by
        )


if __name__ == "__main__":
    show()
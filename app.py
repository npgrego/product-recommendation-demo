import json

from datetime import date


from location import LOCATION_DESCRIPTION, get_exchange_rates, extract_price_currency
from google_client import GoogleClient
from schemas import (
    GoogleShoppingProduct, 
    GoogleShoppingResponse, 
    GoogleShoppingProductOffer, 
    GoogleShoppingProductResponse,
    RecommendedProduct,
    RecommendedProductOffer,
)
import streamlit as st

debug_mode = False

# GOOGLE 2 API

def prepare_recommended_product(google_product: GoogleShoppingProduct, location:str) -> RecommendedProduct:
    exchange_rates: dict[str, float] = st.session_state["exchange_rates"]

    price, currency = extract_price_currency(price=google_product.price, location=location)
    rate = exchange_rates.get(currency, 0) if currency else 0

    return RecommendedProduct(
        id=google_product.product_id,
        title=google_product.title,
        image=google_product.thumbnail,
        has_more_offers=google_product.number_of_comparisons is not None,
        # TODO remove from API
        google_product_link=google_product.product_link,
        offer=RecommendedProductOffer(
            supplier=google_product.source,
            link=google_product.link,
            price=price,
            currency=currency,
            price_uah=round(price*rate, 2) if price else None,
            location=location
        )
    )

def prepare_recommended_product_offer(google_product_offer: GoogleShoppingProductOffer, location:str) -> RecommendedProductOffer:
    exchange_rates: dict[str, float] = st.session_state["exchange_rates"]

    price, currency = extract_price_currency(price=google_product_offer.base_price, location=location)
    rate = exchange_rates.get(currency, 0) if currency else 0

    shipping = tax = 0
    if google_product_offer.additional_price:
        shipping, _ = extract_price_currency(price=google_product_offer.additional_price.shipping, location=location)
        tax, _ = extract_price_currency(price=google_product_offer.additional_price.tax, location=location)

    total_price, _ = extract_price_currency(price=google_product_offer.total_price, location=location)

    return RecommendedProductOffer(
        supplier=google_product_offer.name,
        is_high_quality=google_product_offer.top_quality_store,
        # TODO parse non-google link
        link=google_product_offer.link,
        price=price,
        currency=currency,
        price_uah=round(price*rate, 2) if price is not None else None,
        shipping=shipping,
        tax=tax,
        total_price=total_price,
        total_price_uah=round(total_price*rate, 2) if total_price is not None else None,
        # TODO parse from string
        # delivery_by=None,
        location=location
    )


def get_recommended_products(query:str, location:str, debug_mode: bool) -> list[RecommendedProduct]:
    if debug_mode:
        with open("./example-shopping-products.json", "r") as fp:
            shopping_search_result = GoogleShoppingResponse(**json.load(fp))
            google_products = shopping_search_result.shopping_results 
            # + shopping_search_result.related_shopping_results
            # TODO dedupe
    else:
        google_products = GoogleClient().get_products(query=query, location=location)
    
    return [prepare_recommended_product(google_product=gp, location=location) for gp in google_products]


def get_recommended_product_offers(product_id:str, location:str, debug_mode: bool) -> list[RecommendedProductOffer]:
    
    if debug_mode:
        with open("./example-shopping-product-offers.json", "r") as fp:
            offers = GoogleShoppingProductResponse(**json.load(fp))
            google_product_offers = offers.sellers_results.online_sellers
    else:
        google_product_offers = GoogleClient().get_product_offers(product_id=product_id, location=location)

    return [prepare_recommended_product_offer(google_product_offer=gpo, location=location) for gpo in google_product_offers]
    

def get_more_offers_on_click(product_id:str, location:str, debug_mode: bool):
    st.session_state["recommended_product_offers"] = get_recommended_product_offers(
        product_id=product_id,
        location=location,
        debug_mode=debug_mode
    )


# SHOW

def show_recommended_product_offers(container: st):
    recommended_product_offers:list[RecommendedProductOffer] = st.session_state["recommended_product_offers"]

    for o in recommended_product_offers:
        col_link, col_top, col_details, col_price = container.columns([3,1,3,3])
        
        col_link.markdown(f"[{o.supplier}]({o.link})")
        col_top.write(f"{'⭐' if o.is_high_quality else ''}")
        col_details.write(o.delivery_by)
        
        col_price.text(f"Price: {o.price} {o.currency}, {o.price_uah} UAH \nTotal: {o.total_price} {o.currency}, {o.total_price_uah} UAH")

def show_recommended_products(container: st) -> None:
    recommended_products:list[RecommendedProduct] = st.session_state["recommended_products"]

    for p in recommended_products:

        col_image, col_title, col_link, col_price, col_button = container.columns(5)
        col_image.image(p.image)
        col_title.write(
            f"[{p.offer.location}] {p.title}"
        )
        col_link.markdown(f"[{p.offer.supplier}]({p.offer.link})\n\n[Google Product]({p.google_product_link})")
        col_price.write(f"{p.offer.price} {p.offer.currency} \n{p.offer.price_uah} UAH")
        col_button.button(
            "Get more Offers", 
            key=f"offers_{p.id}", 
            on_click=get_more_offers_on_click, 
            kwargs={"product_id":p.id, "location":p.offer.location, "debug_mode":debug_mode}
        )


def show():

    if "exchange_rates" not in st.session_state:
        st.session_state["exchange_rates"] = get_exchange_rates(date.today())

    if "recommended_products" not in st.session_state:
        st.session_state["recommended_products"] = []
    
    if "recommended_product_offers" not in st.session_state:
        st.session_state["recommended_product_offers"] = []
    
    if "requested_product" not in st.session_state:
        st.session_state["requested_product"] = None

    st.header("Nova Product Search, v0.2.4")

    query = st.text_input("Google Query", value="nike air max 1")
    
    location = st.radio("Location", options=list(LOCATION_DESCRIPTION.keys()), horizontal=True)

    if st.button("Get Products", disabled=not query):
        st.session_state["recommended_products"] = get_recommended_products(query=query, location=location, debug_mode=debug_mode)
        # clean offers
        st.session_state["recommended_product_offers"] = []

    recommended_product_offers_expanded = bool(st.session_state["recommended_product_offers"])
    recommended_products_expanded = bool(st.session_state["recommended_products"]) and not recommended_product_offers_expanded
    

    with st.expander("Recommended products", expanded=recommended_products_expanded):
        recommended_products_container = st.container()
    
    with st.expander("Recommended product offers", expanded=recommended_product_offers_expanded):
        product_offers_container = st.container()
        
    if st.session_state["recommended_products"]:
        show_recommended_products(recommended_products_container)

    if st.session_state["recommended_product_offers"]:
        show_recommended_product_offers(product_offers_container)

    with st.expander("API payload examples v0", expanded=False):
        st.write("### getProducts")
        st.info("{'query':'nike air max 1','location': 'us'}")
        st.write(
            {
                "filters": {
                    "TBD": "TBD"
                },
                "products":[p.model_dump(mode="json") for p in get_recommended_products(query="", location="us", debug_mode=True)]
            }
        )

        st.write("### getProductOffers")
        st.info("{'product_id':'123456','location': 'us'}")
        st.write(
            {
                "product": {
                    "TBD": "Extended product info"
                },
                "offers":[p.model_dump(mode="json") for p in get_recommended_product_offers(product_id="", location="us", debug_mode=True)]
            }
        )

if __name__ == "__main__":
    show()
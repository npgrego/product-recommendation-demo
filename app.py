import json

from datetime import date


from location import LOCATION_DESCRIPTION, get_exchange_rates, get_exchanged_amount
from google_client import GoogleClient
from schemas import (
    GoogleShoppingProduct, 
    GoogleShoppingProductsResponse, 
    GoogleShoppingProductOffer, 
    GoogleShoppingProductResponse,
    RecommendedProduct,
    RecommendedProductOffer,
    ProductFilter,
    ProductFilterValue,
    GetProductResponse,
    GetProductsResponse,
)
import streamlit as st

debug_mode = False

# GOOGLE 2 API

def prepare_recommended_product(google_product: GoogleShoppingProduct, location:str) -> RecommendedProduct:
    exchange_rates: dict[str, float] = st.session_state["exchange_rates"]

    offer = RecommendedProductOffer(
        supplier=google_product.source,
        link=google_product.link,
        price=get_exchanged_amount(
            price=google_product.price, 
            location=location, 
            exchange_rates=exchange_rates
        ),
        location=location
    )

    return RecommendedProduct(
        id=google_product.product_id,
        title=google_product.title,
        images=[google_product.thumbnail],
        has_more_offers=google_product.number_of_comparisons is not None,
        more_offers_text=google_product.number_of_comparisons,
        # TODO remove from API
        google_product_link=google_product.product_link,
        offers=[offer]
    )

def prepare_recommended_product_offer(google_product_offer: GoogleShoppingProductOffer, location:str) -> RecommendedProductOffer:
    exchange_rates: dict[str, float] = st.session_state["exchange_rates"]   

    return RecommendedProductOffer(
        supplier=google_product_offer.name,
        is_high_quality=google_product_offer.top_quality_store,
        # TODO parse non-google link
        link=google_product_offer.link,
        price=get_exchanged_amount(
            price=google_product_offer.base_price, 
            location=location, 
            exchange_rates=exchange_rates
        ),
        shipping=get_exchanged_amount(
            price=google_product_offer.additional_price.shipping, 
            location=location, 
            exchange_rates=exchange_rates
        ) if google_product_offer.additional_price else None,
        tax=get_exchanged_amount(
            price=google_product_offer.additional_price.tax, 
            location=location, 
            exchange_rates=exchange_rates
        ) if google_product_offer.additional_price else None,
        total_price=get_exchanged_amount(
            price=google_product_offer.total_price, 
            location=location, 
            exchange_rates=exchange_rates
        ),
        # TODO parse from string
        # delivery_by=None,
        location=location
    )


def get_recommended_products(query:str, location:str, debug_mode: bool) -> GetProductsResponse:
    if debug_mode:
        with open("./example-shopping-products.json", "r") as fp:
            response = GoogleShoppingProductsResponse(**json.load(fp))
    else:
        response = GoogleClient().get_products(query=query, location=location)

    google_products = response.shopping_results 
    # + response.related_shopping_results
    # TODO dedupe

    filters = []

    for google_filter in response.filters:
        if google_filter.type.lower() == "size":
            filters.append(
                ProductFilter(
                    name="size",
                    values=[
                        ProductFilterValue(text=gfo.text or "10", key=gfo.tbs) 
                        for gfo in google_filter.options
                    ]
                )
            )
    
    products = [prepare_recommended_product(google_product=gp, location=location) for gp in google_products]

    return GetProductsResponse(
        filters=filters,
        products=products
    )

def get_recommended_product(product_id:str, location:str, debug_mode: bool) -> GetProductResponse:
    
    if debug_mode:
        with open("./example-shopping-product.json", "r") as fp:
            response = GoogleShoppingProductResponse(**json.load(fp))
    else:
        response = GoogleClient().get_product(product_id=product_id, location=location)

    selected_filters = []

    for size, size_data in response.product_results.sizes.items():
        if size_data.selected:
            selected_filters.append(
                ProductFilter(
                    name="size",
                    values=[ProductFilterValue(text=size, key=size_data.product_id, is_selected=True)]
                )
            )

    offers = [
        prepare_recommended_product_offer(google_product_offer=gpo, location=location) 
        for gpo in response.sellers_results.online_sellers
    ]

    images = [
        m.link
        for m in response.product_results.media
        if m.type == "image"
    ]

    return GetProductResponse(
        selected_filters=selected_filters,
        product=RecommendedProduct(
            id=response.product_results.product_id,
            title=response.product_results.title,
            images=images,
            offers=offers,
        )
    )
    

def get_more_offers_on_click(product_id:str, location:str, debug_mode: bool):
    st.session_state["recommended_product"] = get_recommended_product(
        product_id=product_id,
        location=location,
        debug_mode=debug_mode
    )


# SHOW

def show_recommended_product_offers(container: st):
    response:GetProductResponse = st.session_state["recommended_product"]

    recommended_product_offers:list[RecommendedProductOffer] = response.product.offers

    for o in recommended_product_offers:
        col_link, col_top, col_details, col_price = container.columns([3,1,3,3])
        
        col_link.markdown(f"[{o.supplier}]({o.link})")
        col_top.write(f"{'⭐' if o.is_high_quality else ''}")
        col_details.write(o.delivery_by)
        
        col_price.text(f"Price: {o.price.original_amount} {o.price.original_currency}, {o.price.amount} UAH \nTotal: {o.total_price.original_amount} {o.total_price.original_currency}, {o.total_price.amount}UAH")

def show_recommended_products(container: st) -> None:
    response:GetProductsResponse = st.session_state["recommended_products"]

    recommended_products:list[RecommendedProduct] = response.products

    for p in recommended_products:

        offer = p.offers[0]

        col_image, col_title, col_link, col_price, col_button = container.columns(5)
        col_image.image(p.images[0])
        col_title.write(
            f"[{offer.location}] {p.title}"
        )
        col_link.markdown(f"[{offer.supplier}]({offer.link})\n\n[Google Product]({p.google_product_link})")
        col_price.write(f"{offer.price.original_amount} {offer.price.original_currency} \n{offer.price.amount} UAH")
        col_button.button(
            "Get more Offers", 
            key=f"offers_{p.id}", 
            on_click=get_more_offers_on_click, 
            kwargs={"product_id":p.id, "location":offer.location, "debug_mode":debug_mode}
        )


def show():

    if "exchange_rates" not in st.session_state:
        st.session_state["exchange_rates"] = get_exchange_rates(date.today())

    if "recommended_products" not in st.session_state:
        st.session_state["recommended_products"] = []
    
    if "recommended_product" not in st.session_state:
        st.session_state["recommended_product"] = []


    st.header("Nova Product Search, v0.2.5")

    query = st.text_input("Google Query", value="nike air max 1")
    
    location = st.radio("Location", options=list(LOCATION_DESCRIPTION.keys()), horizontal=True)

    if st.button("Get Products", disabled=not query):
        st.session_state["recommended_products"] = get_recommended_products(query=query, location=location, debug_mode=debug_mode)
        # clean offers
        st.session_state["recommended_product"] = []

    recommended_product_expanded = bool(st.session_state["recommended_product"])
    recommended_products_expanded = bool(st.session_state["recommended_products"]) and not recommended_product_expanded
    

    with st.expander("Recommended products", expanded=recommended_products_expanded):
        recommended_products_container = st.container()
    
    with st.expander("Recommended product", expanded=recommended_product_expanded):
        recommended_product_container = st.container()
        
    if st.session_state["recommended_products"]:
        show_recommended_products(recommended_products_container)

    if st.session_state["recommended_product"]:
        show_recommended_product_offers(recommended_product_container)

    with st.expander("API payload examples v1", expanded=False):
        st.write("### getProducts")
        st.info("{'query':'nike air max 1','location': 'us'}")
        st.write(get_recommended_products(query="", location="us", debug_mode=True).model_dump(mode="json"))

        st.write("### getProduct")
        st.info("{'product_id':'123456','location': 'us'}")
        st.write(get_recommended_product(product_id="", location="us", debug_mode=True).model_dump(mode="json"))

if __name__ == "__main__":
    show()
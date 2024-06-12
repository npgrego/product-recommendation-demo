import json
from shopping_client import GoogleShoppingClient
from schemas import GoogleShoppingProduct, GoogleShoppingResponse, GoogleShoppingProductOffer, GoogleShoppingProductResponse
import streamlit as st
from urllib.parse import urlparse, parse_qs

def get_google_product_offers(serpapi_product_api):
    parsed_url = urlparse(serpapi_product_api)
    params = {param:vals[0] for param,vals in parse_qs(parsed_url.query).items()}

    st.session_state["google_product_offers"] = GoogleShoppingClient().get_comparisons(params=params)

    # with open("./example-shopping-products.json", "r") as fp:
    #     offers = GoogleShoppingProductResponse(**json.load(fp))
    #     st.session_state["google_product_offers"] = offers.sellers_results.online_sellers

def show_google_product_offers(container: st):
    google_product_offers:list[GoogleShoppingProductOffer] = st.session_state["google_product_offers"]

    for o in google_product_offers:
        col_link, col_top, col_details, col_price = container.columns([3,1,3,3])
        
        col_link.markdown(f"[{o.name}]({o.link})")
        col_top.write(f"{'⭐' if o.top_quality_store else ''}")
        col_details.write(o.details_and_offers[0].text if o.details_and_offers else "")
        
        col_price.text(f"Total: {o.total_price}, \n Base: {o.base_price}")
    

def show_google_products(container: st) -> None:
    google_products:list[GoogleShoppingProduct] = st.session_state["google_products"]

    for c in google_products:

        col_image, col_title, col_link, col_price, col_button = container.columns(5)
        col_image.image(c.thumbnail)
        col_title.write(
            f"⭐{c.rating}({c.reviews}) 🏬{c.store_rating}({c.store_reviews}) {c.title} "
        )
        col_link.markdown(f"[{c.source}]({c.link})\n\n[Google Product]({c.product_link})")
        col_price.write(f"{c.extracted_price}")
        if c.number_of_comparisons:
            col_button.button(
                f"Get {c.number_of_comparisons} Offers", 
                key=f"offers_{c.product_id}", 
                on_click=get_google_product_offers, 
                kwargs={"serpapi_product_api":c.serpapi_product_api}
            )

def show():
    if "google_products" not in st.session_state:
        st.session_state["google_products"] = []
    
    if "google_product_offers" not in st.session_state:
        st.session_state["google_product_offers"] = []

    st.header("Nova Product Search, v0.2.1")
    st.info("Makes google shopping searches for location 'East Hanover,New Jersey,United States'")

    query = st.text_input("Google Query", value="nike air max 1")

    if st.button("Get Products", disabled=not query):
        st.session_state["google_products"] = GoogleShoppingClient().get_candidates(query=query, location="us")
        st.session_state["google_product_offers"] = []
        # with open("./example-shopping.json", "r") as fp:
        #     shopping_search_result = GoogleShoppingResponse(**json.load(fp))
        #     st.session_state["google_products"] = shopping_search_result.shopping_results + shopping_search_result.related_shopping_results

    google_product_offers_expanded = bool(st.session_state["google_product_offers"])
    google_products_expanded = bool(st.session_state["google_products"]) and not google_product_offers_expanded
    

    with st.expander("Google products", expanded=google_products_expanded):
        products_container = st.container()
    
    with st.expander("Google product offers", expanded=google_product_offers_expanded):
        product_offers_container = st.container()
        
    if st.session_state["google_products"]:
        show_google_products(products_container)

    if st.session_state["google_product_offers"]:
        show_google_product_offers(product_offers_container)

if __name__ == "__main__":
    show()
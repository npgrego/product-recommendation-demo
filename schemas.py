from datetime import datetime
from pydantic import BaseModel, Field


# Google Products

class GoogleShoppingProduct(BaseModel):
    title: str
    link: str | None = None
    product_link: str | None = None
    product_id: str | None = None
    serpapi_product_api: str | None = None
    source: str | None = None
    number_of_comparisons: str | None = None
    
    price: str | None = None
    extracted_price: float | None = None
    old_price: str | None = None
    extracted_old_price: float | None = None
    
    rating: float | None = None
    reviews: int | None = None

    thumbnail: str | None = None
    delivery: str | None = None
    
    store_rating: float | None = None
    store_reviews: int | None = None

class GoogleShoppingResponse(BaseModel):
    shopping_results: list[GoogleShoppingProduct] = Field(default_factory=list)
    related_shopping_results: list[GoogleShoppingProduct] = Field(default_factory=list)

# Google Product Offers
class GoogleShoppingProductOfferAdditionalPrice(BaseModel):
    shipping: str | None = None
    tax: str | None = None

class GoogleShoppingProductOfferDedails(BaseModel):
    text: str | None = None

class GoogleShoppingProductOffer(BaseModel):
    name:str
    top_quality_store: bool = False
    link: str | None = None
    details_and_offers: list[GoogleShoppingProductOfferDedails] = Field(default_factory=list)
    base_price: str | None = None
    additional_price: GoogleShoppingProductOfferAdditionalPrice | None = None
    total_price: str | None = None
    offer_id: str | None = None
    offer_link: str | None = None

class GoogleShoppingProductSellerResultsResponse(BaseModel):
    online_sellers: list[GoogleShoppingProductOffer] = Field(default_factory=list)

class GoogleShoppingProductResponse(BaseModel):
    sellers_results: GoogleShoppingProductSellerResultsResponse

# Recommend products API, new approach
class RecommendedProductOffer(BaseModel):
    supplier: str
    is_high_quality: bool = False
    link: str | None = None
    currency: str
    price: float | None = None
    price_uah: float | None = None
    shipping: float | None = None
    tax: float | None = None
    total_price: float | None = None
    total_price_uah: float | None = None
    # TODO parse from string
    delivery_by: datetime | None = Field(default_factory=lambda : datetime.today())
    location: str

class RecommendedProduct(BaseModel):
    id: str
    title: str
    image: str | None = None
    google_product_link: str | None = None
    offer: RecommendedProductOffer
    has_more_offers: bool = False

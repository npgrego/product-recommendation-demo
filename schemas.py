from typing import Optional
from pydantic import BaseModel, Field

class RequestedProduct(BaseModel):
    url: str
    text_content: Optional[str] = None
    html_content: Optional[str] = None
    is_product: bool = False
    summary: Optional[str] = None
    query: Optional[str] = None

    title: Optional[str] = None
    description: Optional[str] = None
    main_image: Optional[str] = None
    price: Optional[float] = None
    currency: Optional[str] = None

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


class CandidateProduct(BaseModel):
    title: str
    position: int | None
    link: str | None = None
    thumbnail: str | None = None
    extracted_price: float | None = None
    price: str | None = None
    rating: float | None = None
    store_rating: float | None = None
    similarity: float = 0

class PreparedCandidateProduct(CandidateProduct):
    currency: str
    price_uah: int | None = None
    is_hidden: bool = False
    location: str

class RecommendProductsResponse(BaseModel):
    products: list[CandidateProduct]

class RecommendProductsRequest(BaseModel):
    product_url: str

class GenerateCandidatesRequest(BaseModel):
    query: str
    main_image: str | None = None
    location: str
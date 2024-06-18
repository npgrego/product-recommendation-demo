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


class GoogleShoppingProductsFilterValue(BaseModel):
    text: str|None = None
    tbs: str

class GoogleShoppingProductsFilter(BaseModel):
    type: str
    options: list[GoogleShoppingProductsFilterValue] = Field(default_factory=list)

class GoogleShoppingProductsResponse(BaseModel):
    filters: list[GoogleShoppingProductsFilter] = Field(default_factory=list)
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

class GoogleShoppingProductDetailsMedia(BaseModel):
    type: str
    link: str

class GoogleShoppingProductDetailsSize(BaseModel):
    product_id: str
    selected: bool = False

class GoogleShoppingProductDetails(BaseModel):
    product_id: str
    title: str
    media: list[GoogleShoppingProductDetailsMedia] = Field(default_factory=list)
    sizes: dict[str, GoogleShoppingProductDetailsSize] = Field(default_factory=dict)


class GoogleShoppingProductResponse(BaseModel):
    product_results: GoogleShoppingProductDetails
    sellers_results: GoogleShoppingProductSellerResultsResponse

# Recommend products API, new approach
class ExchangedAmount(BaseModel):
    amount: float | None = None
    currency: str
    original_amount: float | None = None
    original_currency: str

class RecommendedProductOffer(BaseModel):
    supplier: str | None = None
    is_high_quality: bool = False
    link: str | None = None
    price: ExchangedAmount
    shipping: ExchangedAmount | None = None
    tax: ExchangedAmount | None = None
    total_price: ExchangedAmount | None = None
    # TODO parse from string
    delivery_by: datetime | None = Field(default_factory=lambda : datetime.today())
    location: str

class RecommendedProduct(BaseModel):
    id: str
    title: str
    images: list[str] | None = Field(default_factory=list)
    google_product_link: str | None = None
    offers:list[RecommendedProductOffer] = Field(default_factory=list)
    has_more_offers: bool = False
    more_offers_text: str | None = None

class ProductFilterValue(BaseModel):
    text: str
    key: str
    is_selected: bool = False
    link: str | None = None

class ProductFilter(BaseModel):
    name: str
    values: list[ProductFilterValue]



class GetProductsResponse(BaseModel):
    filters: list[ProductFilter] = Field(default_factory=list)
    products: list[RecommendedProduct]

class GetProductResponse(BaseModel):
    selected_filters: list[ProductFilter] = Field(default_factory=list)
    product: RecommendedProduct
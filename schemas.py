from typing import Optional
from pydantic import BaseModel

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
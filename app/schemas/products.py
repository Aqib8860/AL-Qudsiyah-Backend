from pydantic import BaseModel
from typing import Dict, Any


class ProductBase(BaseModel):
    id: int | None = None
    name: str | None = None
    sale_price: float | None = None
    original_price: float | None = None
    is_available: bool | None = None
    category: str | None = None
    description: str | None = None
    slug: str | None = None
    quantity: int | None = None
    unit: str | None = None


class ProductActionBase(BaseModel):
    name: str | None = None
    sale_price: float | None = None
    original_price: float | None = None
    is_available: bool | None = None
    category: str | None = None
    description: str | None = None
    quantity: int | None = None
    slug: str | None = None
    unit: str | None = None


class ProductImageBase(BaseModel):
    id: int
    image_url: str | None = None
    product_id: int | None = None


class ProductImageActionBase(BaseModel):
    image_url: str | None = None
    product_id: int | None = None


class ProductCategoriesBase(BaseModel):
    category: str | None = None


class AdminProductsListBase(BaseModel):
    id: int | None = None
    name: str | None = None
    sale_price: float | None = None
    original_price: float | None = None
    is_available: bool | None = None
    category: str | None = None
    description: str | None = None
    quantity: int | None = 0
    unit: str | None = None
    image: str | None = None

    class Config:
        from_attributes = True
    
    @classmethod
    async def get_image_data(cls, product: Dict[str, Any]):
        if product:
            product.image = product.images[0].image_url if product.images else None
        return product if product else None


class ProductsListBase(BaseModel):
    id: int | None = None
    name: str | None = None
    sale_price: float | None = None
    original_price: float | None = None
    is_available: bool | None = None
    category: str | None = None
    description: str | None = None
    image: str | None = None

    class Config:
        from_attributes = True
    
    @classmethod
    async def get_image_data(cls, product: Dict[str, Any]):
        if product:
            product.image = product.images[0].image_url if product.images else None
        return product if product else None


class ProductsDetailBase(BaseModel):
    id: int | None = None
    name: str | None = None
    sale_price: float | None = None
    original_price: float | None = None
    is_available: bool | None = None
    category: str | None = None
    description: str | None = None
    slug: str | None = None
    image: str | None = None
    quantity: int | None = None
    unit: str | None = None

    class Config:
        from_attributes = True
    
    @classmethod
    async def get_image_data(cls, product: Dict[str, Any]):
        if product:
            product.image = product.images[0].image_url if product.images else None
        return product if product else None



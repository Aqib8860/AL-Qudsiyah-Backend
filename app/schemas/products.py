from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime


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
    in_stock: int | None = None
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
    in_stock: int | None = None


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
    in_stock: int | None = None
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
    quantity: int | None = None
    unit: str | None = None

    class Config:
        from_attributes = True
    
    @classmethod
    async def get_response_data(cls, product: Dict[str, Any]):
        return product if product else None


class CatProductBase(BaseModel):
    id: int | None = None
    name: str | None = None
    sale_price: float | None = None
    original_price: float | None = None
    is_available: bool | None = None
    category: str | None = None
    description: str | None = None
    image: str | None = None
    quantity: int | None = 1

    class Config:
        from_attributes = True
    
    @classmethod
    async def get_image_data(cls, product: Dict[str, Any]):
        if product:
            product.image = product.images[0].image_url if product.images else None
        return product if product else None


class UserCartBase(BaseModel):
    id: int | None = None
    products: list[CatProductBase] | None = []


class AddToCartBase(BaseModel):
    product_id: int
    quantity: int | None = 1


class PincodeBase(BaseModel):
    id: int | None = None
    pincode: str
    active: bool | None = False


class CreateOrderBase(BaseModel):
    id: int | None = None
    product_id: int | None = None
    address: str | None = None
    created_on: datetime | None = None


class OrderBase(BaseModel):
    id: int | None = None
    product_id: int | None = None
    address: str | None = None
    total_amount: int | None = None
    user_id: int | None = None
    status: str | None = None
    created_on: datetime | None = None


class UserOrderBase(BaseModel):
    id: int | None = None
    product_id: int | None = None
    product_name: str | None = None
    address: str | None = None
    total_amount: int | None = None
    user_id: int | None = None
    image: str | None = None
    status: str | None = None
    created_on: datetime | None = None
    
    class Config:
        from_attributes = True
    
    @classmethod
    async def get_image_data(cls, order: Dict[str, Any]):
        if order.product:
            order.image = order.product.images[0].image_url if order.product.images else None
            order.product_name = order.product.name if order.product else None
        return order if order else None


class CheckoutBase(BaseModel):
    customer_phone: str
    address: str
    

class CashfreeWebhookBase(BaseModel):
    data: dict | None = None


class PaymentBase(BaseModel):
    id: int | None = None
    products: str | None = None
    address: str | None = None
    customer_phone: str | None = None
    amount_paid: float | None = None
    paid_on: datetime | None = None
    transaction_no: str | None = None
    orders: str | None = None
    payment_method: str | None = None
    status: str | None = None
    created_on: datetime | None = None


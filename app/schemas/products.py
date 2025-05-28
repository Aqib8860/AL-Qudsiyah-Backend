from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime, date
from crud.utils import get_order_payment_details

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


class UpdatePincodeBase(BaseModel):
    active: bool


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


class AdminOrderBase(BaseModel):
    id: int | None = None
    product_id: int | None = None
    product_name: str | None = None
    image: str | None = None
    address: str | None = None
    total_amount: int | None = None
    user_id: int | None = None
    username: str | None = None
    status: str | None = None
    delivery_status: str | None = None
    created_on: datetime | None = None

    class Config:
        from_attributes = True
    
    @classmethod
    async def get_data(cls, order: Dict[str, Any]):
        if order and order.product:
            order.image = order.product.images[0].image_url if order.product.images else None
            order.product_name = order.product.name if order.product else None
            if order.user:
                order.username = f"{order.user.first_name} {order.user.last_name} "

        return order if order else None


class AdminOrderDetailBase(BaseModel):
    id: int | None = None
    product_id: int | None = None
    product_name: str | None = None
    image: str | None = None
    address: str | None = None
    total_amount: int | None = None
    user_id: int | None = None
    username: str | None = None
    status: str | None = None
    delivery_status: str | None = None
    created_on: datetime | None = None
    payment_detail: dict | None = None

    class Config:
        from_attributes = True
    
    @classmethod
    async def get_data(cls, order: Dict[str, Any], db):
        if order and order.product:
            order.image = order.product.images[0].image_url if order.product.images else None
            order.product_name = order.product.name if order.product else None
            if order.user:
                order.username = f"{order.user.first_name} {order.user.last_name} "
        
                # Get Payment Details
                order.payment_detail = await get_order_payment_details(db, order)

        return order if order else None


class LatestOrdersBase(BaseModel):
    id: int | None = None
    product_name: str | None = None
    image: str | None = None
    total_amount: int | None = None
    username: str | None = None
    status: str | None = None
    created_on: datetime | None = None

    class Config:
        from_attributes = True
    
    @classmethod
    async def get_data(cls, order: Dict[str, Any]):
        if order and order.product:
            order.image = order.product.images[0].image_url if order.product.images else None
            order.product_name = order.product.name if order.product else None
            if order.user:
                order.username = f"{order.user.first_name} {order.user.last_name} "

        return order if order else None


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
    promocode: str | None = None
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


class AddProductRatingReviewBase(BaseModel):
    product_id: int
    rating: float | None = 0
    review: str | None = None


class ProductRatingReviewBase(BaseModel):
    id: int | None = None
    product_id: int | None = None
    rating: float | None = 0
    review: str | None = None
    username: dict | None = None
    added_on: datetime | None = None
    
    class Config:
        from_attributes = True
    
    @staticmethod
    async def get_data(product):
        if product and product.user_id:

            return {
            "id": product.id,
            "product_id": product.product_id,
            "username": f"{product.user.first_name} {product.user.last_name if product.user.last_name else ''}",
            "rating": product.rating,
            "review": product.reveiew,
            "added_on": str(product.added_on)
        }
            

class PromocodeActionBase(BaseModel):
    promocode: str | None = None
    products: str | None = None
    discount_type: str | None = None
    amount: int | None = None
    available: bool | None = None
    quantity: int | None = None
    expired_on: datetime | None = None


class PromocodeBase(BaseModel):
    id: int | None = None
    promocode: str | None = None
    products: str | None = None
    discount_type: str | None = None
    created_by: int | None = None
    created_by_name: str | None = None
    amount: int | None = None
    available: bool | None = None
    quantity: int | None = None
    expired_on: date | None = None
    created_on: datetime | None = None

    class Config:
        from_attributes = True
    
    @classmethod
    async def get_data(cls, promocode: Dict[str, Any]):
        if promocode and promocode.created_by:
            promocode.created_by_name = f"{promocode.user.first_name} {promocode.user.last_name}"
        return promocode if promocode else None


class PageSectionBase(BaseModel):
    id: int | None = None
    page_url: str | None = None
    name: str | None = None
    image_url: str | None = None


class UserOrderDetailBase(BaseModel):
    id: int | None = None
    product_id: int | None = None
    product_name: str | None = None
    image: str | None = None
    address: str | None = None
    total_amount: int | None = None
    user_id: int | None = None
    username: str | None = None
    status: str | None = None
    delivery_status: str | None = None
    created_on: datetime | None = None
    payment_detail: dict | None = None

    class Config:
        from_attributes = True
    
    @classmethod
    async def get_data(cls, order: Dict[str, Any], db):
        if order and order.product:
            order.image = order.product.images[0].image_url if order.product.images else None
            order.product_name = order.product.name if order.product else None
            if order.user:
                order.username = f"{order.user.first_name} {order.user.last_name} "
        
                # Get Payment Details
                order.payment_detail = await get_order_payment_details(db, order)

        return order if order else None

import pytz
from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, Float, DateTime, Date
from sqlalchemy.orm import relationship
from datetime import datetime

from .database import Base

IST = pytz.timezone("Asia/Kolkata")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=True)
    sale_price = Column(Float, default=0)
    original_price = Column(Float, default=0)
    is_available = Column(Boolean, default=False)
    is_giftset = Column(Boolean, default=False)
    category = Column(String, index=True, nullable=True)
    description = Column(Text, nullable=True)
    slug = Column(String, index=True, nullable=True)
    quantity = Column(Integer, default=0)
    unit = Column(String, nullable=True)
    rating = Column(Float, default=0)
    in_stock = Column(Integer, default=0)

    # Add this line to fix the error
    images = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")
    rating_review = relationship("RatingReview", back_populates="product_rating_review", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="product", cascade="all, delete-orphan")
    

    # Many-to-many relationship with Cart
    carts = relationship("Cart", secondary="product_cart_association", back_populates="products")
    
    


class Cart(Base):
    __tablename__ = "cart"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    user = relationship("User", back_populates="carts")
    # Many to many relationship with Product
    products = relationship("Product", secondary="product_cart_association", back_populates="carts")
    

# To store multiple products in cart
class ProductCartAssociation(Base):
    __tablename__ = "product_cart_association"

    product_id = Column(Integer, ForeignKey("products.id"), primary_key=True)
    cart_id = Column(Integer, ForeignKey("cart.id"), primary_key=True)
    quantity = Column(Integer, default=1)


class ProductImage(Base):
    __tablename__ = "product_images"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    image_url = Column(String, nullable=True)

    product = relationship("Product", back_populates="images")


class RatingReview(Base):
    __tablename__ = "rating_review"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    rating = Column(Float, default=0)
    reveiew = Column(Text, nullable=True)
    added_on = Column(DateTime, default=datetime.now(), nullable=True)

    product_rating_review = relationship("Product", back_populates="rating_review")
    user = relationship("User", back_populates="rating_review")


class Pincode(Base):
    __tablename__ = "pincode"
    
    id = Column(Integer, primary_key=True, index=True)
    pincode = Column(String, index=True, nullable=True)
    active = Column(Boolean, default=False)



class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    address = Column(Text, nullable=True)
    total_amount = Column(Text, nullable=True)
    status = Column(String, default="PENDING", nullable=True)
    cancellation_reason = Column(Text, nullable=True)
    cancellation_date = Column(DateTime, nullable=True)
    delivery_status = Column(String, default="PENDING", nullable=True)
    created_on = Column(DateTime, default=datetime.now(IST), nullable=True)

    product = relationship("Product", back_populates="orders")
    user = relationship("User", back_populates="orders")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)
    cart_id = Column(Integer, nullable=True)
    products = Column(String, nullable=True)
    orders = Column(String, nullable=True)
    promocode = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    customer_phone = Column(String, nullable=True)
    amount_paid = Column(Integer, nullable=True)
    payment_method = Column(String, nullable=True)
    paid_on = Column(DateTime, nullable=True)
    transaction_no = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(String, default="PENDING", nullable=True)
    created_on = Column(DateTime, default=datetime.now(IST), nullable=True)

    user = relationship("User", back_populates="payments")

class PaymentWebhook(Base):
    __tablename__ = "payment_webhook"

    id = Column(Integer, primary_key=True)
    data = Column(Text, nullable=True)


class Promocode(Base):
    __tablename__ = "promocode"

    id = Column(Integer, primary_key=True)
    promocode = Column(String, nullable=True)
    products = Column(String, nullable=True, default="ALL")
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    discount_type = Column(String, nullable=True, default="PERCENTAGE")
    amount = Column(Integer, nullable=True, default=0)
    available = Column(Boolean, default=False)
    quantity = Column(Integer, default=0)
    expired_on = Column(Date, nullable=True)
    created_on = Column(DateTime, default=datetime.now(IST), nullable=True)

    user = relationship("User", back_populates="promocodes")


class PageSection(Base):
    __tablename__ = "pagesection"
    id = Column(Integer, primary_key=True)
    page_url = Column(String, nullable=True)
    name = Column(String, nullable=True)
    image_url = Column(String, nullable=True)

    
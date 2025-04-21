from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, Float
from sqlalchemy.orm import relationship

from .database import Base



class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=True)
    sale_price = Column(Float, default=0)
    original_price = Column(Float, default=0)
    is_available = Column(Boolean, default=False)
    category = Column(String, index=True, nullable=True)
    description = Column(Text, nullable=True)
    slug = Column(String, index=True, nullable=True)
    quantity = Column(Integer, default=0)
    unit = Column(String, nullable=True)
    in_stock = Column(Integer, default=0)

    # Add this line to fix the error
    images = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")
    rating_review = relationship("RatingReview", back_populates="product_rating_review", cascade="all, delete-orphan")
    
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
    rating = Column(Float, default=0)
    reveiew = Column(Text, nullable=True)

    product_rating_review = relationship("Product", back_populates="rating_review")


class Pincode(Base):
    __tablename__ = "pincode"
    id = Column(Integer, primary_key=True, index=True)
    pincode = Column(String, index=True, nullable=True)
    active = Column(Boolean, default=False)



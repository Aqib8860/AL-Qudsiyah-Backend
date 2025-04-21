import io
from fastapi import UploadFile
from sqlalchemy.orm import selectinload
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse

from .file_upload import upload_to_s3
from models.products import Product, ProductImage, Cart, ProductCartAssociation, Pincode
from schemas.products import (
    ProductActionBase, AdminProductsListBase, ProductsListBase,  AddToCartBase, PincodeBase)

# ------------------------------------- Product ----------------------------------------------------------------

async def create_product(db: Session, product: ProductActionBase):
    try:

        db_product = Product(
            name=product.name, original_price=product.original_price,
            sale_price=product.sale_price,
            is_available=product.is_available,
            category=product.category,
            description=product.description,
            slug=product.slug,
            quantity=product.quantity,
            unit=product.unit,
            in_stock=product.in_stock

        )
        
        db.add(db_product)    
        db.commit()
        db.refresh(db_product)
        
        return db_product
    except Exception as e:
        db.rollback()
        return JSONResponse({"error": str(e)}, status_code=400)


# Products List
async def get_all_products(db: Session, limit: int, category: str):
    query = db.query(Product).order_by(Product.id.desc()).options(selectinload(Product.images))

    if category:
        query = query.filter(Product.category == category)

    products = query.limit(limit).all()
    return [await ProductsListBase.get_image_data(product) for product in products]



async def get_product_view(db: Session, product_id: int):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return JSONResponse(status_code=404, content={"detail": "Product not found"})
    return product


async def admin_products_list_view(db: Session, get_image: bool, name:str, category:str):
    query = db.query(Product)
    
    if name:
        query = query.filter(Product.name.ilike(f"%{name}%"))

    if category:
        query = query.filter(Product.category == category)

    products =  query.order_by(Product.id).options(selectinload(Product.images)).all()

    if get_image:
        return [await AdminProductsListBase.get_image_data(product) for product in products]
    else: return products


# Update Product
async def update_product_view(db:Session, product_id: int, product_data:ProductActionBase):
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return JSONResponse(status_code=404, content={"detail": "Product not found"})
        
        # Update only the fields provided in the request
        for field, value in product_data.model_dump(exclude_unset=True).items():
            setattr(product, field, value)
        
        db.commit()
        db.refresh(product)
        
        return product
    except Exception as e:
        db.rollback()
        return JSONResponse({"detail": str(e)}, status_code=400)


async def delete_product_view(db: Session, product_id:int):
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return JSONResponse(status_code=404, content={"detail": "Product not found"})
        
        db.delete(product)
        db.commit()
        
        return {"detail": "Product deleted successfully"}
    except Exception as e:
        return JSONResponse({"detail": str(e)}, status_code=400)


# Get Product Categoris
async def get_product_categories_view(db: Session):
    try:
        return db.query(Product.category).distinct().all()
    except Exception as e:
        return JSONResponse({"detail": str(e)}, status_code=400)

# =================================================================================================================


# ------------------------------------- Product Image -------------------------------------------------------------

# Add Product Image
async def add_product_image_view(db, product_id, image):
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return JSONResponse(status_code=404, content={"detail": "Product not found"})
        
        current_time = datetime.now()
        timestamp = datetime.timestamp(current_time)

        image_url = f"al-qudsiyah/{int(timestamp)}_{image.filename}"

        file_content = await image.read()
        
        file_obj = io.BytesIO(file_content)

        file_aws_url = upload_to_s3(file_obj, image_url, image.content_type)
        
        db_product_image = ProductImage(
            image_url=file_aws_url,
            product_id=product_id
        )
        
        db.add(db_product_image)
        db.commit()
        db.refresh(db_product_image)
        
        return db_product_image
    except Exception as e:
        db.rollback()
        return JSONResponse({"detail": str(e)}, status_code=400)
    

# Get product Image
async def get_product_images_view(db: Session, product_id: int):
    # we can also return product.image if we have product obj
    try:
        return db.query(ProductImage).filter(ProductImage.product_id == product_id).all()
    except Exception as e:
        return JSONResponse({"detail": str(e)}, status_code=400)


async def delete_product_image_view(db:Session, image_id:int):
    try:
        product_image = db.query(ProductImage).filter(ProductImage.id == image_id).first()
        if not product_image:
            return JSONResponse(status_code=404, content={"detail": "Product Image not found"})
        
        db.delete(product_image)
        db.commit()
        
        return {"detail": "Product Image deleted successfully"}
    except Exception as e:
        db.rollback()
        return JSONResponse({"detail": str(e)}, status_code=400)
# =================================================================================================================


async def user_cart_view(db: Session, user: dict):
    cart = db.query(Cart).filter(Cart.user_id == user["id"]).first()
    
    if not cart:
        db_cart = Cart(user_id=user["id"])
        db.add(db_cart)
        db.commit()
        db.refresh(db_cart)    
        user_cart = db.query(Cart).filter(Cart.user_id == user["id"]).first()
        
    if not cart.products:
        return JSONResponse({
        "cart_id": cart.id,
        "products": []
    })

    products_data = [
        {
            "id": product.id,
            "name": product.name,
            "sale_price": product.sale_price,
            "original_price": product.original_price,
            "slug": product.slug,
            "in_stock": product.in_stock,
            "unit": product.unit,
            "description": product.description,
            "image": product.images[0].image_url if product.images else None
        }
        for product in cart.products
    ]

    return JSONResponse({
        "cart_id": cart.id,
        "products": products_data
    })


async def add_to_cart_view(db: Session, user: dict, cart: AddToCartBase):
    # Get User Cart
    user_cart = db.query(Cart).filter(Cart.user_id == user["id"]).first()
    # If user not have cart then create
    if not user_cart:
        db_cart = Cart(user_id=user["id"])
        db.add(db_cart)
        db.commit()
        db.refresh(db_cart)    
        user_cart = db.query(Cart).filter(Cart.user_id == user["id"]).first()

    # Check product in already in cart
    product_cart = db.query(ProductCartAssociation).filter(
        ProductCartAssociation.product_id== cart.product_id, 
        ProductCartAssociation.cart_id == user_cart.id
        ).first()
    if product_cart:
        return JSONResponse({"error": "Item already in cart"}, status_code=400)
    
    # Add Product in cart
    db_product_cart = ProductCartAssociation(product_id=cart.product_id, cart_id=user_cart.id)

    db.add(db_product_cart)
    db.commit()
    db.refresh(db_product_cart)    
    
    return JSONResponse({"msg": "Product Added to Cart"})
    
    # product_cart = ProductCartAssociation(cart_id=db)

        
async def delete_from_cart_view(db: Session, user: dict, product_id: int):
    # Get User Cart
    user_cart = db.query(Cart).filter(Cart.user_id == user["id"]).first()

    prodcut_cart = db.query(ProductCartAssociation).filter(
        ProductCartAssociation.cart_id == user_cart.id,
        ProductCartAssociation.product_id == product_id,
    ).first()
    
    if prodcut_cart:
        db.delete(prodcut_cart)
        db.commit()

    return JSONResponse({"msg": "Item removed from cart"}, status_code=200)


async def add_pincode_view(db: Session, user: dict, pincode_data: PincodeBase):
    try:
        exists = db.query(Pincode).filter(Pincode.pincode == pincode_data.pincode).first()
        if exists:
            return JSONResponse({"msg": "Pincode already exists"}, status_code=400)

        db_pincode = Pincode(pincode=pincode_data.pincode, active=pincode_data.active)
        db.add(db_pincode)
        db.commit()
        db.refresh(db_pincode)

        return JSONResponse({"msg": "Pincode Added"})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)


async def pincodes_list_view(db: Session, user: dict):
    pincodes = db.query(Pincode)
    return pincodes


async def check_pincode_delivery_view(db: Session, pincode: str):
    availabilty = db.query(Pincode).filter(Pincode.pincode == pincode, Pincode.active == True).first()
    return JSONResponse({"available": True if availabilty else False})

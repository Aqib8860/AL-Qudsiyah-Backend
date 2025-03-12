import io
from fastapi import UploadFile
from sqlalchemy.orm import selectinload
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse

from .file_upload import upload_to_s3
from models.products import Product, ProductImage
from schemas.products import ProductActionBase, AdminProductsListBase, ProductsListBase, ProductBase, ProductsDetailBase

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
            unit=product.unit
        )
        
        db.add(db_product)    
        db.commit()
        db.refresh(db_product)
        
        return db_product
    except Exception as e:
        db.rollback()
        return JSONResponse({"detail": str(e)}, status_code=400)


# Products List
async def get_all_products(db: Session):
    query = db.query(Product)
    products =  query.order_by(Product.id.desc()).options(selectinload(Product.images)).all()
    return [await ProductsListBase.get_image_data(product) for product in products]



async def get_product_view(db: Session, product_id: int):
    product = db.query(Product).filter(Product.id == product_id).options(selectinload(Product.images)).first()
    if not product:
        return JSONResponse(status_code=404, content={"detail": "Product not found"})
    
    return await ProductsDetailBase.get_image_data(product)


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


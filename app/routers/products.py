from fastapi import APIRouter, Depends, Form, UploadFile, File
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from models.database import SessionLocal
from schemas.products import ProductActionBase, ProductBase, ProductImageBase, ProductCategoriesBase, AdminProductsListBase, ProductsListBase, ProductBase, ProductsDetailBase
from crud.products import (
    create_product, get_all_products, add_product_image_view, get_product_images_view, get_product_categories_view, delete_product_view,  update_product_view, delete_product_image_view,
    admin_products_list_view, get_product_view
)

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------- Product ---------------------------------------------------------------

@router.get("/")
async def get_no_found(db: Session = Depends(get_db)):
    return JSONResponse(status_code=404, content={"detail": "Page not found"})


#  Add Product
@router.post("/product/", response_model=ProductBase)
async def create_new_product(product: ProductActionBase, db: Session = Depends(get_db)):
    return await create_product(db=db, product=product)


# Get Products List
@router.get("/products-list/", response_model=list[ProductsListBase])
async def get_products_list(db: Session = Depends(get_db)):
    return await get_all_products(db=db)


# Get Products List - Admin Only
@router.get("/admin-dashboard/products-list/", response_model=list[AdminProductsListBase])
async def admin_products_list(
    get_image: bool = False,
    name: str | None = None,
    category: str = None,
    db: Session = Depends(get_db)
):
    return await admin_products_list_view(db=db, get_image=get_image, name=name, category=category)


# Retrive Product
@router.get("/product/{product_id}", response_model=ProductsDetailBase)
async def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    return await get_product_view(db=db, product_id=product_id)


# Update Product
@router.patch("/product/{product_id}/", response_model=ProductBase)
async def update_product(
    product_id: int, 
    product_data: ProductActionBase,
    db: Session = Depends(get_db)):
    return await update_product_view(db=db, product_id=product_id, product_data=product_data)
 

# Delete Product
@router.delete("/product/{product_id}/")
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    return await delete_product_view(db=db, product_id=product_id)
# ===============================================================================================


# Product Categories List
@router.get("/product-categories/", response_model=list[ProductCategoriesBase])
async def get_product_categories(db: Session = Depends(get_db)):
    return await get_product_categories_view(db=db)

# ===============================================================================================


# ---------------------- Product Image ----------------------------------------------------------
# Get Product Image 
@router.get("/product-images/{product_id}/", response_model=list[ProductImageBase])
async def get_product_images(product_id: int, db: Session = Depends(get_db)):
    return await get_product_images_view(db=db, product_id=product_id)


# Add Product Image
@router.post("/product-image/", response_model=ProductImageBase)
async def add_product_image(
    product_id: str = Form(),
    image: UploadFile = Form(),
    db: Session = Depends(get_db)
):
    return await add_product_image_view(db, product_id, image)


# Delete Product Image
@router.delete("/product-image/{image_id}/")
async def delete_product_image(image_id: int, db: Session = Depends(get_db)):
    # - Reamining Delete Image from AWS
    return await delete_product_image_view(db=db, image_id=image_id)

# =================================================================================================


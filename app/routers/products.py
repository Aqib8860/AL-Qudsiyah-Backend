from fastapi import APIRouter, Depends, Form, UploadFile, File, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from models.database import SessionLocal

from schemas.products import (
    ProductActionBase, ProductBase, ProductImageBase, ProductCategoriesBase, AdminProductsListBase, ProductsListBase, ProductBase, ProductsDetailBase, UserCartBase, AddToCartBase, 
    PincodeBase, OrderBase, CreateOrderBase, CheckoutBase
    )

from crud.auth import get_current_user
from crud.products import (
    create_product, get_all_products, add_product_image_view, get_product_images_view, get_product_categories_view, delete_product_view,  update_product_view, delete_product_image_view,
    admin_products_list_view, get_product_view, user_cart_view, add_to_cart_view, delete_from_cart_view, add_pincode_view, pincodes_list_view, check_pincode_delivery_view, add_order_view,
    checkout_view, cashfree_view
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
async def get_products_list(
    limit: int = Query(10, ge=1), 
    category: str | None = None,
    db: Session = Depends(get_db)):
    return await get_all_products(db=db, limit=limit, category=category)


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


#--------------------------------------------------------------------------------------------------
# User Cart 
@router.get("/user/cart/", response_model=UserCartBase)
async def user_cart(
    user: dict = Depends(get_current_user), 
    db: Session = Depends(get_db)):
    
    return await user_cart_view(db=db, user=user)


@router.post("/product/add-to-cart/", response_model=UserCartBase)
async def add_to_cart(
    cart_data: AddToCartBase,
    user: dict = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    return await add_to_cart_view(db=db, user=user, cart=cart_data)


@router.delete("/user/cart/{product_id}/")
async def delete_from_cart(
    product_id: int,
    user: dict = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    return await delete_from_cart_view(db=db, user=user, product_id=product_id)

# ========================================================================================================

# Pincode
@router.post("/admin/pincode/", response_model=PincodeBase)
async def add_pincode(
    pincode_data: PincodeBase,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return await add_pincode_view(db=db, user=user, pincode_data=pincode_data)


@router.get("/admin/pincodes/", response_model=list[PincodeBase])
async def pincodes_list(
    user: dict = Depends(get_current_user), 
    db: Session = Depends(get_db)):
    
    return await pincodes_list_view(db=db, user=user)


# Check Delviry Available
@router.get("/check-delivery/{pincode}/")
async def check_pincode_delivery(
    pincode: str,
    db: Session = Depends(get_db)):
    
    return await check_pincode_delivery_view(db=db, pincode=pincode)


# -------Order ---------------------
@router.post("/user/order/", response_model=OrderBase)
async def add_order(
    order: CreateOrderBase,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return await add_order_view(db=db, order=order, user=user)


# Checkout ----------------------------------------------
@router.post("/user/checkout/")
async def checkout(
    checkout_data: CheckoutBase,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)    
):
    return await checkout_view(db=db, user=user, checkout_data=checkout_data)


# Cashfree order -----------------------------------------
@router.post("/create/order/")
async def cashfree_order(
    db: Session = Depends(get_db)
):
    return await cashfree_view(db=db)


# Payments

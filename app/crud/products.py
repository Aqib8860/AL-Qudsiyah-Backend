import io
import os
import requests
from fastapi import UploadFile
from typing import Dict
from sqlalchemy.orm import selectinload
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from .file_upload import upload_to_s3
from .orders import do_orders_success

from models.products import (
    Product, ProductImage, Cart, ProductCartAssociation, Pincode, Order, Payment, PaymentWebhook, RatingReview, Promocode, PageSection
    )

from schemas.products import (
    ProductActionBase, AdminProductsListBase, ProductsListBase,  AddToCartBase, PincodeBase, OrderBase, CreateOrderBase, CheckoutBase,
    UserOrderBase, AddProductRatingReviewBase, ProductRatingReviewBase, AdminOrderBase, AdminOrderDetailBase, LatestOrdersBase, 
    UpdatePincodeBase, PromocodeActionBase, PromocodeBase
)


load_dotenv()

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


async def get_product_category_view(db: Session, product_id: int):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return JSONResponse(status_code=404, content={"detail": "Product not found"})
    return JSONResponse({"category": product.category})


async def admin_products_list_view(db: Session, get_image: bool, name:str, category:str):
    query = db.query(Product)
    
    if name:
        query = query.filter(Product.name.ilike(f"%{name}%"))

    if category:
        query = query.filter(Product.category == category)

    products =  query.order_by(Product.id.desc()).options(selectinload(Product.images)).all()

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
        cart = db.query(Cart).filter(Cart.user_id == user["id"]).first()
        
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
            "quantity": product.quantity,
            "image": product.images[0].image_url if product.images else None
        }
        for product in cart.products
    ]

    return JSONResponse({
        "cart_id": cart.id,
        "products": products_data
    })


# User cart items count
async def user_cart_items_count(db: Session, user: dict):
    cart = db.query(Cart).filter(Cart.user_id == user["id"]).first()
    
    if not cart:
        db_cart = Cart(user_id=user["id"])
        db.add(db_cart)
        db.commit()
        db.refresh(db_cart)    
        cart = db.query(Cart).filter(Cart.user_id == user["id"]).first()
    
    product_count = len(cart.products) if cart.products else 0
    
    
    return JSONResponse({"count": product_count}, status_code=200)


async def add_to_cart_view(db: Session, user: dict, cart: AddToCartBase):
    try:
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
            return JSONResponse({"msg": "Item already in cart"}, status_code=200)
        
        # Add Product in cart
        db_product_cart = ProductCartAssociation(product_id=cart.product_id, cart_id=user_cart.id, quantity=cart.quantity)

        db.add(db_product_cart)
        db.commit()
        db.refresh(db_product_cart)    
        
        return JSONResponse({"msg": "Product Added to Cart"})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)
    
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


# Update Pincode
async def update_pincode_view(db: Session, pincode_id:int, pincode_data: UpdatePincodeBase):
    try:
        pincode_obj = db.query(Pincode).filter(Pincode.id == pincode_id).first()
        if not pincode_obj:
            return JSONResponse({"msg": "Pincode not found"}, status_code=404)

        pincode_obj.active = pincode_data.active
        db.commit()
        db.refresh(pincode_obj)

        return JSONResponse({"msg": "Pincode updated successfully"})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)
    

# Pincodes List
async def pincodes_list_view(db: Session, user: dict):
    pincodes = db.query(Pincode)
    return pincodes


async def check_pincode_delivery_view(db: Session, pincode: str):
    availabilty = db.query(Pincode).filter(Pincode.pincode == pincode, Pincode.active == True).first()
    return JSONResponse({"available": True if availabilty else False})


# Orders List -------------------------------------------------------------
async def user_orders_list_view(db: Session, user: dict):
    orders = db.query(Order).filter(Order.user_id == user["id"]).order_by(Order.id.desc())
    if orders:
        return [await UserOrderBase.get_image_data(order) for order in orders]

    return JSONResponse([])


async def orders_list_view(db: Session):
    orders = db.query(Order).order_by(Order.id.desc())
    if orders:
        return [await AdminOrderBase.get_data(order) for order in orders]

    return JSONResponse([])


# Get Order Details for admin
async def admin_order_detail_view(db: Session, order_id: int):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        return JSONResponse({"error": "Order not exists"}, status_code=404)
    
    return await AdminOrderDetailBase.get_data(order, db)


# Get Order Counts
async def admin_orders_count_view(db: Session):
    try:
        return JSONResponse({
            "total_orders": db.query(Order).count(),
            "pending_orders": db.query(Order).filter(Order.status == "PENDING").count(),
            "success_orders": db.query(Order).filter(Order.status == "SUCCESS").count(),
            "delivery_pending": db.query(Order).filter(Order.delivery_status == "PENDING").count(),
            "delivery_success": db.query(Order).filter(Order.delivery_status == "SUCCESS").count(),
        })
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)


async def admin_latest_orders_view(db: Session, status: str):
    orders = db.query(Order).filter(Order.status == status).order_by(Order.created_on.desc()).limit(5)
    if orders:
        return [await LatestOrdersBase.get_data(order) for order in orders]
    return JSONResponse([])


# Add Order
async def add_order_view(db: Session, order: CreateOrderBase, user: dict):
    product = db.query(Product).filter(id=order.product_id).first()
    if not product:
        return JSONResponse({"error": "Product not exists"}, status_code=404)

    db_order = Order(
        product_id=order.product_id, 
        user_id=user["id"],
        address=order.address,
        total_amount=product.sale_price
    )

    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    return db_order


async def checkout_view(db: Session, user: dict, checkout_data: CheckoutBase):
    print("Checkout data ", checkout_data)
    # Get user cart
    cart = db.query(Cart).filter(Cart.user_id == user['id']).first()
    if not cart:
        return JSONResponse({"error": "Cart not exists"}, status_code=404)
    
    # If cart does not have product
    if not cart.products:
        return JSONResponse({"error": "Cart is empty"}, status_code=400)
    
    # Check if promocode used
    promocode_discount_percentage = 0
    if checkout_data.promocode:
        promocode = db.query(Promocode).filter(Promocode.promocode == checkout_data.promocode).first()

        # Check promocode validity
        if promocode.expired_on < datetime.now().date():
            return JSONResponse({"message": "Promocode expired"}, status_code=400)
        
        if promocode.quantity <= 0 or not promocode.available: 
            return JSONResponse({"message": "Promocode is not available"}, status_code=400)
        
        promocode.quantity = promocode.quantity - 1
        promocode_discount_percentage = promocode.amount
        db.commit()

        
    total_amount = 0
    orders = ""

    for product in cart.products:

        # Create Order   
        db_order = Order(
            product_id=product.id, 
            user_id=user["id"],
            address=checkout_data.address,
            total_amount=product.sale_price
        )
        db.add(db_order)
        db.commit()
        db.refresh(db_order)

        # Calculate Total Price
        total_amount += product.sale_price
        if orders:
            orders += f",{db_order.id}"
        else:
            orders += f"{db_order.id}"

    # If promocode applied then less the amount
    if promocode_discount_percentage:
        discount_amount = (total_amount * promocode_discount_percentage) / 100
        total_amount = total_amount - discount_amount

    # Add Payment
    db_payment = Payment(
        amount_paid=total_amount, orders=orders, address=checkout_data.address, 
        customer_phone=checkout_data.customer_phone, user_id= user['id'], 
        promocode=checkout_data.promocode
    )

    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)

    # Cashfree Data
    url = "https://sandbox.cashfree.com/pg/orders"
    payload = {
        "order_currency": "INR",
        "order_amount": total_amount,
        "order_tags": {
            "payment_id": str(db_payment.id),
        },
        "customer_details": {
            "customer_id": f"{user["id"]}",
            "customer_phone": checkout_data.customer_phone
        },
        "order_meta": {
            "return_url": os.environ.get("CASHFREE_REDIRECT_URL"),
        }
    }
    
    headers = {
        "x-api-version": os.environ.get("CASHFREE_API_VERSION"),
        "x-client-id": os.environ.get("CASHFREE_CLIENT_ID"),
        "x-client-secret": os.environ.get("CASHFREE_CLIENT_SECRET"),
        "Content-Type": "application/json"
    }

    response = requests.post(url=url, json=payload, headers=headers)
    
    if response.status_code != 200:
        return JSONResponse(response.json(), status_code=response.status_code)
    
    cashfree_data = response.json()

    db_payment.transaction_no = cashfree_data["order_id"]
    db.commit()
    db.refresh(db_payment)

    
    return JSONResponse({"session_id": cashfree_data["payment_session_id"]})


async def cashfree_webhook_view(db: Session, data: dict):
    data = data.model_dump()

    db_payment_webhook = PaymentWebhook(data=str(data))
    db.add(db_payment_webhook)
    db.commit()

    if not "data" in data.keys():
        return
    
    data = data["data"]

    if not "payment" in data.keys():
        return    
    
    order = data["order"]
    cashfree_payment = data["payment"]

    payment_id = order["order_tags"]["payment_id"]

    # Get Payment
    payment = db.query(Payment).filter(Payment.id == int(payment_id)).first()

    # Payment - Success or User Drop - User Drop Validation Remaaining
    payment.status = cashfree_payment["payment_status"]
    payment.paid_on = cashfree_payment["payment_time"]
    db.commit()
    db.refresh(payment)

    if payment.status == "SUCCESS":
        await do_orders_success(db, payment)

    return


async def payments_view(db: Session):
    payments = db.query(Payment).order_by(Payment.id.desc())
    return payments


async def cashfree_view(db: Session):
    url = "https://sandbox.cashfree.com/pg/orders"
    payload = {
        "order_currency": "INR",
        "order_amount": 10.34,
        "customer_details": {
            "customer_id": "7112AAA812234",
            "customer_phone": "9898989898"
        }
    }
    
    headers = {
        "x-api-version": "2025-01-01",
        "x-client-id": "2416424c2b8b07903c54c9c530246142",
        "x-client-secret": "TEST5e8ce57ea8d7f0736cb8b68ce3798e787fc974de",
        "Content-Type": "application/json"
    }

    response = requests.post(url=url, json=payload, headers=headers)

    return JSONResponse(response.json(), status_code=response.status_code)


async def product_rating_review_view(db: Session, product_id: int):
    # try:
    product_ratings = db.query(RatingReview).filter(RatingReview.product_id == product_id).all()

    if not product_ratings:
        return JSONResponse(
            status_code=200,
            content={
                "average": 0,
                "total_reviews": 0,
                "breakdown": {5: 0, 4: 0, 3: 0, 2: 0, 1: 0},
                "reviews": [],
            },
        )

    if product_ratings:
        # Calculate average rating
        total_reviews = len(product_ratings)
        total_score = sum([r.rating for r in product_ratings])
        average_rating = total_score / total_reviews

        # Rating breakdown
        breakdown: Dict[int, int] = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
        for r in product_ratings:
            rating = int(round(r.rating))
            if rating in breakdown:
                breakdown[rating] += 1

        # Format individual reviews
        reviews = [await ProductRatingReviewBase.get_data(r) for r in product_ratings]
        return JSONResponse(
        status_code=200,
        content={
            "average": round(average_rating, 1),
            "totalReviews": total_reviews,
            "breakdown": breakdown,
            "reviews": reviews,
        },
    )
        # return [await ProductRatingReviewBase.get_data(rating) for rating in product_ratings]

    # except Exception as e:
    #     return JSONResponse({"error": str(e)}, status_code=400)


async def add_product_rating_view(db: Session, user: dict, data: AddProductRatingReviewBase):
    try:
        data = data.model_dump()
        
        product = db.query(Product).filter(Product.id == data['product_id']).first()
        if not product:
            return JSONResponse({"error": "Product not exists"}, status_code=404)
        # Add data in table

        product_rating = db.query(RatingReview).filter(
            RatingReview.product_id == data["product_id"],
            RatingReview.user_id == user["id"]
        ).first()

        if not product_rating:
            product_rating = RatingReview(
                product_id=data["product_id"],
                user_id=user["id"],
                rating=data["rating"],
                reveiew=data["review"]
            )

            db.add(product_rating)
            db.commit()    

            return JSONResponse({"msg": "Success"})
        
        if data.get("rating", None):
            product_rating.rating = data["rating"]

        if data.get("review", None):
            product_rating.reveiew = data["review"]

        db.commit()
        return JSONResponse({"msg": "Success"})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)
    

# Promocodes List
async def promocodes_list_view(db: Session):
    promocodes = db.query(Promocode).order_by(Promocode.created_on.desc()).all()
    if promocodes:
        return [await PromocodeBase.get_data(promocode) for promocode in promocodes]
    return JSONResponse([])


# Add Promocode
async def add_promocode_view(db: Session, user: dict, promocode: PromocodeActionBase):
    try:
        promocode_data = promocode.model_dump()

        promocode = db.query(Promocode).filter(Promocode.promocode == promocode_data["promocode"]).first()
        if promocode:
            return JSONResponse({"message": "Promocode already exists"}, status_code=400)

        db_promocode = Promocode(
            promocode=promocode_data["promocode"],
            created_by=user["id"],
            amount=promocode_data["amount"],
            available=promocode_data["available"],
            quantity=promocode_data["quantity"],
            expired_on=promocode_data["expired_on"]
        )

        db.add(db_promocode)
        db.commit()

        return JSONResponse({"message": "Success"})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)
    
    
# Update Promocode
async def update_promocode_view(db: Session, promocode_id: int, promocode: PromocodeActionBase):
    try:
        promocode_data = promocode.model_dump(exclude_unset=True)

        db_promocode = db.query(Promocode).filter(Promocode.id == promocode_id).first()

        if not db_promocode:
            return JSONResponse({"message": "Promocode not found"}, status_code=404)
        
        # Check if the promocode name is being updated to a name that already exists
        if "promocode" in promocode_data:
            existing = (
                db.query(Promocode)
                .filter(Promocode.promocode == promocode_data["promocode"], Promocode.id != promocode_id)
                .first()
            )
            if existing:
                return JSONResponse({"message": "Promocode with this name already exists"}, status_code=400)


        for key, value in promocode_data.items():
            setattr(db_promocode, key, value)

        db.commit()
        db.refresh(db_promocode)

        return JSONResponse({"message": "Promocode updated successfully"})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)

    

# Apply Promocode
async def apply_promocode_view(db: Session, promocode: str):
    try:
        promocode = db.query(Promocode).filter(Promocode.promocode == promocode).first()

        if not promocode:
            return JSONResponse({"message": "Invalid Promocode"}, status_code=400)
        
        if promocode.expired_on < datetime.now().date():
            return JSONResponse({"message": "Promocode expired"}, status_code=400)

        if not promocode.available or promocode.quantity <= 0:
            return JSONResponse({"message": "Promocode not available"}, status_code=400)

        return JSONResponse({"message": "Promocode Applied"})
    
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)


# Get Promocode
async def get_promocode_view(db: Session, promocode: str):
    promocode = db.query(Promocode).filter(Promocode.promocode == promocode).first()
    
    if not promocode:
        return JSONResponse({"message": "Invalid Promocode"}, status_code=400)

    return promocode


# Delete Promocode
async def delete_promocode_view(db: Session, promocode_id: int):
    try:
        db_promocode = db.query(Promocode).filter(Promocode.id == promocode_id).first()

        if not db_promocode:
            return JSONResponse({"messgae": "Promocode not found"}, status_code=404)

        db.delete(db_promocode)
        db.commit()

        return JSONResponse({"message": "Promocode deleted successfully"}, status_code=200)

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)


# Page Section -------------------------------------
async def get_page_section_view(db, page_url, name):
    query = db.query(PageSection)

    if page_url:
        query = query.filter(PageSection.page_url == page_url)

    if name:
        query = query.filter(PageSection.name == name)

    return query.all()


async def add_page_section_view(db, page_url, name, image):
    try: 
        page_section_exists = db.query(PageSection).filter(PageSection.name == name).first()
        if page_section_exists:
            return JSONResponse({"message": "Name already exists"}, status_code=400)
        
        current_time = datetime.now()
        timestamp = datetime.timestamp(current_time)

        image_url = f"page-section/{int(timestamp)}_{image.filename}"

        file_content = await image.read()
        
        file_obj = io.BytesIO(file_content)

        file_aws_url = upload_to_s3(file_obj, image_url, image.content_type)
        
        db_page_section = PageSection(
            page_url=page_url, name=name, image_url=file_aws_url
        )
        
        db.add(db_page_section)
        db.commit()
        db.refresh(db_page_section)
        
        return JSONResponse({"message": "Page Section Created"}, status_code=200)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)
    

# Update Page Section
async def update_page_section_view(db, pagesection_id, page_url, name, image):
    try:
        # Get existing section
        page_section = db.query(PageSection).filter(PageSection.id == pagesection_id).first()
        if not page_section:
            return JSONResponse({"message": "Page section not found"}, status_code=404)

        # Check if name is changing and already exists
        # if name and name != page_section.name:
        #     existing = db.query(PageSection).filter(PageSection.name == name).first()
        #     if existing:
        #         return JSONResponse({"message": "Name already exists"}, status_code=400)
        #     page_section.name = name

        if page_url:
            page_section.page_url = page_url

        if image:
            current_time = datetime.now()
            timestamp = datetime.timestamp(current_time)
            image_url = f"page-section/{int(timestamp)}_{image.filename}"

            file_content = await image.read()
            file_obj = io.BytesIO(file_content)

            file_aws_url = upload_to_s3(file_obj, image_url, image.content_type)
            page_section.image_url = file_aws_url

        db.commit()
        db.refresh(page_section)

        return JSONResponse({"message": "Page Section Updated"}, status_code=200)

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)
    

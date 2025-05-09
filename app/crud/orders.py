from models.products import Order, Cart, ProductCartAssociation
from models.users import User
from .send_mail import send_order_confirm_mail


async def do_orders_success(db, payment):
    payment_orders = payment.orders.split(",")
    payment_orders = [int(order_id) for order_id in payment_orders]  # Convert to int 

    orders = db.query(Order).filter(Order.id.in_(payment_orders)).all()
    products_name = []
    for order in orders:
        order.status = "SUCCESS"
        products_name.append(order.product.name)

    db.commit()
    
    user_cart = db.query(Cart).filter(Cart.user_id == payment.user_id).first()
    ordered_product_ids = [order.product_id for order in orders]

    db.query(ProductCartAssociation).filter(
        ProductCartAssociation.cart_id == user_cart.id,
        ProductCartAssociation.product_id.in_(ordered_product_ids)
    ).delete(synchronize_session=False)

    db.commit()
    
    

    await send_order_confirm_mail(payment, order, products_name)
    return


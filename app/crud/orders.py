from models.products import Order
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
    
    await send_order_confirm_mail(payment, order, products_name)
    return


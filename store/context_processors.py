# # store/context_processors.py
# from decimal import Decimal

# def cart_total(request):
#     cart = request.session.get("cart", {})
#     total = Decimal("0.00")
#     for item in cart.values():
#         quantity = item.get("quantity", 0)
#         price = Decimal(item.get("price", "0.00"))
#         total += price * quantity
#     return {"cart_total": total}

from decimal import Decimal

def cart_total(request):
    cart = request.session.get("cart", {})
    total = Decimal("0.00")
    for item in cart.values():
        total += Decimal(item.get("price", "0.00")) * item.get("quantity", 0)
    return {"cart_total": total}
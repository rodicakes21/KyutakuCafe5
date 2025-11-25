from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Product, Order, CheckoutItem
from .cart import Cart  # Your custom Cart class
from django.utils import timezone
# from django.shortcuts import redirect
# from django.views.decorators.http import require_POST
from decimal import Decimal



# @require_POST
# def admin_logout(request):
#     logout(request)
#     return redirect('home')




# Home page / product list
def home(request):
    products = Product.objects.all()
    return render(request, "store/home.html", {"products": products})


# Product detail page
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, "store/product_detail.html", {"product": product})


# --------------------------
# CART VIEWS — now open to everyone
# --------------------------

def cart_view(request):
    cart = Cart(request)
    return render(request, "store/cart.html", {"cart": cart})


def cart_add(request, pk):
    cart = Cart(request)
    product = get_object_or_404(Product, pk=pk)
    cart.add(product=product)
    return redirect("cart")


def cart_remove(request, pk):
    cart = Cart(request)
    product = get_object_or_404(Product, pk=pk)
    cart.remove(product)
    return redirect("cart")


def cart_increase(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, pk=product_id)
    cart.add(product=product, quantity=1)
    return redirect("cart")


def cart_decrease(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, pk=product_id)
    cart.add(product=product, quantity=-1)

    item = cart.cart.get(str(product_id))
    if item and item["quantity"] <= 0:
        cart.remove(product)

    return redirect("cart")


# --------------------------
# USER LOGIN / REGISTER / LOGOUT
# --------------------------

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'store/login.html')


def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return redirect('register')

        User.objects.create_user(username=username, email=email, password=password1)
        messages.success(request, "Account created! You can now log in.")
        return redirect('login')

    return render(request, 'store/register.html')


def logout_view(request):
    logout(request)
    return redirect('home')


# --------------------------
# CHECKOUT — now allowed without login
# --------------------------

def checkout_view(request):
    cart = request.session.get("cart", {})

    if not cart:
        messages.error(request, "Your cart is empty.")
        return redirect("cart")

    products = Product.objects.filter(id__in=cart.keys())

    cart_items = []
    cart_total = Decimal("0.00")

    for product in products:
        raw_value = cart.get(str(product.id))

        # -----------------------------------------------------
        # SAFE QUANTITY HANDLER
        # Accepts:
        #   3 → OK
        #   "3" → OK
        #   {"quantity": 3} → OK
        # -----------------------------------------------------
        if isinstance(raw_value, dict):
            quantity = int(raw_value.get("quantity", 1))
        else:
            quantity = int(raw_value)

        total_price = product.price * quantity

        cart_items.append({
            "product": product,
            "quantity": quantity,
            "total_price": total_price
        })

        cart_total += total_price

    # -----------------------------
    # Process POST — PLACE ORDER
    # -----------------------------
    if request.method == "POST":
        name = request.POST.get("name")
        address = request.POST.get("address")
        email = request.POST.get("email")
        phone = request.POST.get("phone")

        # Create the order with default PENDING (model default)
        order = Order.objects.create(
            customer_name=name,
            address=address,
            email=email,
            phone=phone
        )

        for item in cart_items:
            CheckoutItem.objects.create(
                order=order,
                product=item["product"],
                quantity=item["quantity"],
                total_price=item["total_price"]
            )

        # Save to guest receipts session
        guest_orders = request.session.get("guest_orders", [])
        guest_orders.append(order.id)
        request.session["guest_orders"] = guest_orders
        request.session.modified = True

        # Clear cart
        request.session["cart"] = {}
        request.session.modified = True

        return redirect("guest_receipts")

    return render(request, "store/checkout.html", {
        "cart_items": cart_items,
        "cart_total": cart_total
    })

# --------------------------
# RECEIPT VIEW
# Allow:
#   Admin → sees ALL receipts
#   Authenticated user → sees only THEIR receipts
#   Guest → sees receipts only if NOT linked to any user
# --------------------------

def receipt_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    # If the order belongs to a logged-in customer
    if order.user:
        if not request.user.is_authenticated:
            return redirect("login")

        if order.user != request.user:
            messages.error(request, "You cannot view someone else's receipt.")
            return redirect("home")

    # Guest order: order.user == None → allow access
    return render(request, 'store/receipt.html', {'order': order})



# ABOUT PAGE
def about_view(request):
    return render(request, "store/about.html")


# CONTACT PAGE
def contact_view(request):
    return render(request, "store/contact.html")


def my_receipts(request):
    if not request.user.is_authenticated:
        messages.error(request, "You must log in to view your receipts.")
        return redirect("login")

    orders = Order.objects.filter(user=request.user).order_by("-created_at")

    return render(request, "store/my_receipts.html", {"orders": orders})

def receipt_guest_view(request, code):
    order = get_object_or_404(Order, receipt_code=code)
    return render(request, "store/receipt.html", {"order": order})


def receipt_lookup_view(request):
    if request.method == "POST":
        code = request.POST.get("receipt_code")
        return redirect("receipt_guest", code=code)
    return render(request, "store/receipt_lookup.html")

def guest_receipts_view(request):
    guest_orders = request.session.get("guest_orders", [])

    # Convert to int safely
    guest_orders = [int(x) for x in guest_orders if str(x).isdigit()]

    # Get actual orders that exist
    orders = Order.objects.filter(id__in=guest_orders)

    # Auto-clean: keep only UNPAID / PENDING orders
    valid_ids = []
    for order in orders:
        if order.payment_status != "paid":
            valid_ids.append(order.id)

    # Replace session with cleaned list
    request.session["guest_orders"] = valid_ids
    request.session.modified = True

    # Display only unpaid/pending orders to guest
    orders = Order.objects.filter(id__in=valid_ids)

    return render(request, "store/guest_receipts.html", {
        "orders": orders
    })




def guest_payment_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    # Only allow payment if order belongs to this guest session
    guest_receipts = request.session.get("guest_receipts", [])
    if order.id not in guest_receipts:
        messages.error(request, "You are not allowed to pay for this receipt.")
        return redirect("guest_receipts")

    if request.method == "POST":
        reference = request.POST.get("reference")
        screenshot = request.FILES.get("screenshot")

        order.payment_reference = reference
        order.payment_screenshot = screenshot
        order.payment_status = "pending"
        order.save()

        messages.success(request, "Payment submitted! Admin will verify it.")
        return redirect("guest_receipts")

    return render(request, "store/guest_payment.html", {"order": order})

from decimal import Decimal
from django.shortcuts import get_object_or_404, redirect

def save_guest_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == "POST":
        from decimal import Decimal

        cash = Decimal(request.POST.get("cash", "0"))
        change = Decimal(request.POST.get("change", "0"))

        # Mark as PAID
        order.cash_received = cash
        order.change_given = change
        order.payment_status = "paid"
        order.save()

        # Remove this order from guest session list
        guest_orders = request.session.get("guest_orders", [])

        # Convert safely
        guest_orders = [int(x) for x in guest_orders if str(x).isdigit()]

        # Remove the paid order
        if order.id in guest_orders:
            guest_orders.remove(order.id)

        request.session["guest_orders"] = guest_orders
        request.session.modified = True

        # Redirect to guest receipts page (your request)
        return redirect("guest_receipts")

    return redirect("guest_receipts")



def admin_all_receipts(request):
    if not request.user.is_staff:
        messages.error(request, "Admin access only.")
        return redirect("home")

    orders = Order.objects.all().order_by("-printed_at", "-created_at")

    return render(request, "store/admin_receipts.html", {"orders": orders})


# def save_guest_payment(request, order_id):
#     if request.method != "POST":
#         return redirect("guest_receipts")

#     guest_receipts = request.session.get("guest_receipts", [])

#     # Security: only allow orders from this browser session
#     if order_id not in guest_receipts:
#         messages.error(request, "Unauthorized access.")
#         return redirect("guest_receipts")

#     order = get_object_or_404(Order, id=order_id)

#     # Save cash & change
#     cash = float(request.POST.get("cash"))
#     change = float(request.POST.get("change"))

#     order.cash_received = cash
#     order.change_given = change
#     order.payment_status = "paid"
#     order.printed_at = timezone.now()
#     order.save()

#     # Remove from guest session receipts
#     guest_receipts.remove(order_id)
#     request.session["guest_receipts"] = guest_receipts

#     messages.success(request, "Payment submitted successfully!")

#     # Redirect to the remaining receipts
#     return redirect("guest_receipts")

def admin_login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user and user.is_superuser:
            login(request, user)
            return redirect("admin_receipts")
        else:
            messages.error(request, "Invalid admin login.")

    return render(request, "store/admin_login.html")


def admin_receipts_view(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        messages.error(request, "Admin access only.")
        return redirect("admin_login")

    orders = Order.objects.all().order_by("-created_at")

    return render(request, "store/admin_receipts.html", {"orders": orders})


def delete_receipt(request, order_id):
    if not request.user.is_superuser:
        messages.error(request, "Admin access only.")
        return redirect("admin_login")

    order = get_object_or_404(Order, id=order_id)
    order.delete()

    messages.success(request, "Receipt deleted successfully.")
    return redirect("admin_receipts")


def admin_logout(request):
    logout(request)
    return redirect('home')

def cashier_payment_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == "POST":
        cash = Decimal(request.POST.get("cash", "0"))
        change = Decimal(request.POST.get("change", "0"))

        order.cash_received = cash
        order.change_given = change
        order.payment_status = "paid"
        order.save()

        return redirect("receipt", order_id=order.id)

    return render(request, "store/guest_payment.html", {
        "order": order
    })

def cashier_receipt_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, "store/mini_cashier_receipt.html", {"order": order})

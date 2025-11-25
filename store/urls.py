from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),

    # Products
    path("product/<int:pk>/", views.product_detail, name="product_detail"),

    # Cart
    path("cart/", views.cart_view, name="cart"),
    path("cart/add/<int:pk>/", views.cart_add, name="cart_add"),
    path("cart/remove/<int:pk>/", views.cart_remove, name="cart_remove"),
    path("cart/increase/<int:product_id>/", views.cart_increase, name="cart_increase"),
    path("cart/decrease/<int:product_id>/", views.cart_decrease, name="cart_decrease"),

    # Checkout
    path("checkout/", views.checkout_view, name="checkout"),

    # Receipt Pages
    path("receipt/<int:order_id>/", views.receipt_view, name="receipt"),
    path("receipt-code/<str:code>/", views.receipt_guest_view, name="receipt_guest"),

    # path("receipt-code/<str:code>/", views.receipt_guest_view, name="receipt_guest"),
    # path("find-receipt/", views.receipt_lookup_view, name="receipt_lookup"),

    # Receipt lookup (guest)
    path("find-receipt/", views.receipt_lookup_view, name="receipt_lookup"),

    # Customer receipt list
    path("my-receipts/", views.my_receipts, name="my_receipts"),

    # Pages
    path("about/", views.about_view, name="about"),
    path("contact/", views.contact_view, name="contact"),

    # Auth
    path("login/", views.login_view, name="login"),
    # path("register/", views.register_view, name="register"),
    # path("logout/", views.logout_view, name="logout"),

    path("guest-receipts/", views.guest_receipts_view, name="guest_receipts"),

    path("guest-receipts/pay/<int:order_id>/", views.guest_payment_view, name="guest_payment"),

    path("guest-receipt/<int:order_id>/save-payment/", views.save_guest_payment, name="save_guest_payment"),

    path("admin/receipts/", views.admin_all_receipts, name="admin_receipts"),
    path("admin-login/", views.admin_login_view, name="admin_login"),
    path("admin-receipts/", views.admin_receipts_view, name="admin_receipts"),
    path("admin-receipts/delete/<int:order_id>/", views.delete_receipt, name="delete_receipt"),

    # path("admin-logout/", views.admin_logout, name="admin_logout"),



    

    path(
    "guest-receipt/<int:order_id>/pay/",
    views.guest_payment_view,
    name="guest_pay"
),

    path(
    "guest-receipt/<int:order_id>/save-payment/",
    views.save_guest_payment,
    name="save_guest_payment"
),

    path('admin_logout/', views.admin_logout, name='admin_logout'),

    # path("cashier/payment/<int:order_id>/", views.cashier_payment_view, name="cashier_payment"),

    path("cashier/payment/<int:order_id>/", views.cashier_payment_view, name="cashier_payment"),

    path("cashier/receipt/<int:order_id>/", views.cashier_receipt_view, name="cashier_receipt"),








]

from django.contrib import admin
from .models import Product, Order, CheckoutItem


class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "customer_name", "email", "phone", "created_at", "get_total_price")
    readonly_fields = ("created_at",)

    def get_total_price(self, obj):
        return obj.total_price()

    get_total_price.short_description = "Total Price"


# Register models
admin.site.register(Product)
admin.site.register(Order, OrderAdmin)
admin.site.register(CheckoutItem)

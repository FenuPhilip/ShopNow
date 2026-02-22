from django.contrib import admin
from .models import Cart, CartItem, Coupon


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['line_total']

    def line_total(self, obj):
        return obj.line_total


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'session_key', 'total_items', 'subtotal', 'updated_at']
    inlines = [CartItemInline]

    def total_items(self, obj):
        return obj.total_items

    def subtotal(self, obj):
        return obj.subtotal


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_type', 'discount_value', 'is_active', 'valid_from', 'valid_to', 'used_count']
    list_filter = ['is_active', 'discount_type']
    search_fields = ['code']
    list_editable = ['is_active']

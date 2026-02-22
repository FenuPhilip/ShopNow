from django.contrib import admin
from .models import Order, OrderItem, Payment, OrderStatusHistory


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['line_total']


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0


class StatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ['changed_at']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'total', 'status', 'payment_status', 'created_at']
    list_filter = ['status', 'payment_status', 'created_at']
    search_fields = ['order_number', 'user__email', 'shipping_name']
    list_editable = ['status']
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    inlines = [OrderItemInline, PaymentInline, StatusHistoryInline]
    fieldsets = (
        ('Order Info', {'fields': ('order_number', 'user', 'status', 'payment_status', 'notes')}),
        ('Shipping', {'fields': ('shipping_name', 'shipping_address_line1', 'shipping_address_line2',
                                  'shipping_city', 'shipping_state', 'shipping_postal_code',
                                  'shipping_country', 'shipping_phone')}),
        ('Pricing', {'fields': ('subtotal', 'discount_amount', 'shipping_cost', 'total', 'coupon')}),
        ('Tracking', {'fields': ('tracking_number', 'delivered_at')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )

    def save_model(self, request, obj, form, change):
        if change:
            old_obj = Order.objects.get(pk=obj.pk)
            if old_obj.status != obj.status:
                OrderStatusHistory.objects.create(
                    order=obj, status=obj.status, note=f'Status changed by admin'
                )
        super().save_model(request, obj, form, change)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['order', 'payment_method', 'amount', 'status', 'transaction_id', 'created_at']
    list_filter = ['status', 'payment_method']
    search_fields = ['order__order_number', 'transaction_id']

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from .models import Order, OrderItem, Payment, OrderStatusHistory
from .forms import CheckoutForm, PaymentForm
from cart.views import get_or_create_cart
from cart.models import CartItem, Coupon
from users.models import Address


@login_required
def checkout_view(request):
    cart = get_or_create_cart(request)
    if cart.is_empty:
        messages.warning(request, 'Your cart is empty.')
        return redirect('cart')

    addresses = Address.objects.filter(user=request.user)
    coupon_code = request.session.get('coupon_code')
    coupon = None
    discount = 0

    if coupon_code:
        try:
            coupon = Coupon.objects.get(code=coupon_code)
            if coupon.is_valid():
                discount = coupon.calculate_discount(cart.subtotal)
        except Coupon.DoesNotExist:
            pass

    shipping_cost = 0
    total = cart.subtotal - discount + shipping_cost

    if request.method == 'POST':
        form = CheckoutForm(request.POST, user=request.user)
        if form.is_valid():

            request.session['checkout_data'] = {
                'address_id': form.cleaned_data.get('address_id'),
                'shipping_name': form.cleaned_data['shipping_name'],
                'address_line1': form.cleaned_data['address_line1'],
                'address_line2': form.cleaned_data.get('address_line2', ''),
                'city': form.cleaned_data['city'],
                'state': form.cleaned_data['state'],
                'postal_code': form.cleaned_data['postal_code'],
                'country': form.cleaned_data['country'],
                'phone': form.cleaned_data['phone'],
                'notes': form.cleaned_data.get('notes', ''),
            }
            return redirect('payment')
    else:

        default_address = addresses.filter(address_type='shipping', is_default=True).first()
        initial = {}
        if default_address:
            initial = {
                'shipping_name': default_address.full_name,
                'address_line1': default_address.address_line1,
                'address_line2': default_address.address_line2,
                'city': default_address.city,
                'state': default_address.state,
                'postal_code': default_address.postal_code,
                'country': default_address.country,
                'phone': default_address.phone,
            }
        form = CheckoutForm(initial=initial, user=request.user)

    context = {
        'form': form,
        'cart': cart,
        'addresses': addresses,
        'coupon': coupon,
        'discount': discount,
        'shipping_cost': shipping_cost,
        'total': total,
    }
    return render(request, 'orders/checkout.html', context)


@login_required
def payment_view(request):
    cart = get_or_create_cart(request)
    checkout_data = request.session.get('checkout_data')

    if cart.is_empty or not checkout_data:
        return redirect('checkout')

    coupon_code = request.session.get('coupon_code')
    coupon = None
    discount = 0
    if coupon_code:
        try:
            coupon = Coupon.objects.get(code=coupon_code)
            if coupon.is_valid():
                discount = coupon.calculate_discount(cart.subtotal)
        except Coupon.DoesNotExist:
            pass

    shipping_cost = 0
    total = cart.subtotal - discount + shipping_cost

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment_method = form.cleaned_data['payment_method']
            with transaction.atomic():

                order = Order.objects.create(
                    user=request.user,
                    shipping_name=checkout_data['shipping_name'],
                    shipping_address_line1=checkout_data['address_line1'],
                    shipping_address_line2=checkout_data.get('address_line2', ''),
                    shipping_city=checkout_data['city'],
                    shipping_state=checkout_data['state'],
                    shipping_postal_code=checkout_data['postal_code'],
                    shipping_country=checkout_data['country'],
                    shipping_phone=checkout_data['phone'],
                    notes=checkout_data.get('notes', ''),
                    subtotal=cart.subtotal,
                    discount_amount=discount,
                    shipping_cost=shipping_cost,
                    total=total,
                    coupon=coupon,
                    status='confirmed' if payment_method == 'cod' else 'pending',
                    payment_status='pending',
                )


                for item in cart.items.select_related('product').all():
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        product_name=item.product.name,
                        product_sku=item.product.sku,
                        unit_price=item.product.effective_price,
                        quantity=item.quantity,
                    )

                    item.product.stock -= item.quantity
                    item.product.save(update_fields=['stock'])


                Payment.objects.create(
                    order=order,
                    payment_method=payment_method,
                    amount=total,
                    status='success' if payment_method == 'cod' else 'pending',
                )


                OrderStatusHistory.objects.create(order=order, status=order.status, note='Order placed')


                if coupon:
                    coupon.used_count += 1
                    coupon.save(update_fields=['used_count'])
                    del request.session['coupon_code']


                cart.items.all().delete()


                if 'checkout_data' in request.session:
                    del request.session['checkout_data']

            messages.success(request, f'Order #{order.order_number} placed successfully!')
            return redirect('order_confirmation', order_number=order.order_number)
    else:
        form = PaymentForm()

    context = {
        'form': form,
        'cart': cart,
        'discount': discount,
        'shipping_cost': shipping_cost,
        'total': total,
        'checkout_data': checkout_data,
    }
    return render(request, 'orders/payment.html', context)


@login_required
def order_confirmation_view(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    return render(request, 'orders/order_confirmation.html', {'order': order})


@login_required
def order_list_view(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items')
    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)
    return render(request, 'orders/order_list.html', {
        'orders': orders,
        'status_choices': Order.STATUS_CHOICES,
        'current_status': status_filter,
    })


@login_required
def order_detail_view(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    status_history = order.status_history.all()
    payments = order.payments.all()
    return render(request, 'orders/order_detail.html', {
        'order': order,
        'status_history': status_history,
        'payments': payments,
    })


@login_required
def cancel_order_view(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    if order.status in ['pending', 'confirmed']:
        order.status = 'cancelled'
        order.save(update_fields=['status'])
        OrderStatusHistory.objects.create(order=order, status='cancelled', note='Cancelled by customer')

        for item in order.items.all():
            if item.product:
                item.product.stock += item.quantity
                item.product.save(update_fields=['stock'])
        messages.success(request, f'Order #{order.order_number} has been cancelled.')
    else:
        messages.error(request, 'This order cannot be cancelled.')
    return redirect('order_detail', order_number=order_number)

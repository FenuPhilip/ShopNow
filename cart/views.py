from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Cart, CartItem, Coupon
from store.models import Product


def get_or_create_cart(request):
    
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)

        if created and request.session.session_key:
            try:
                guest_cart = Cart.objects.get(session_key=request.session.session_key)
                for item in guest_cart.items.all():
                    cart_item, item_created = CartItem.objects.get_or_create(
                        cart=cart, product=item.product,
                        defaults={'quantity': item.quantity}
                    )
                    if not item_created:
                        cart_item.quantity += item.quantity
                        cart_item.save()
                guest_cart.delete()
            except Cart.DoesNotExist:
                pass
        return cart
    else:
        if not request.session.session_key:
            request.session.create()
        cart, created = Cart.objects.get_or_create(session_key=request.session.session_key)
        return cart


def cart_detail_view(request):
    cart = get_or_create_cart(request)
    items = cart.items.select_related('product').all()
    coupon = None
    discount = 0
    coupon_code = request.session.get('coupon_code')
    if coupon_code:
        try:
            coupon = Coupon.objects.get(code=coupon_code)
            if coupon.is_valid():
                discount = coupon.calculate_discount(cart.subtotal)
            else:
                del request.session['coupon_code']
                coupon = None
        except Coupon.DoesNotExist:
            pass

    total = cart.subtotal - discount
    context = {
        'cart': cart,
        'items': items,
        'coupon': coupon,
        'discount': discount,
        'total': total,
    }
    return render(request, 'cart/cart.html', context)


@require_POST
def add_to_cart_view(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    quantity = int(request.POST.get('quantity', 1))

    if not product.is_in_stock:
        messages.error(request, f'"{product.name}" is out of stock.')
        return redirect('product_detail', slug=product.slug)

    cart = get_or_create_cart(request)
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart, product=product,
        defaults={'quantity': quantity}
    )
    if not created:
        cart_item.quantity += quantity
        cart_item.save()
        messages.success(request, f'Updated "{product.name}" quantity in cart.')
    else:
        messages.success(request, f'"{product.name}" added to cart!')

    next_url = request.POST.get('next', request.META.get('HTTP_REFERER', 'cart'))
    return redirect(next_url)


@require_POST
def update_cart_view(request, item_id):
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    quantity = int(request.POST.get('quantity', 1))
    if quantity <= 0:
        cart_item.delete()
        messages.info(request, 'Item removed from cart.')
    else:
        cart_item.quantity = quantity
        cart_item.save()
        messages.success(request, 'Cart updated.')
    return redirect('cart')


def remove_from_cart_view(request, item_id):
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    cart_item.delete()
    messages.info(request, 'Item removed from cart.')
    return redirect('cart')


@require_POST
def apply_coupon_view(request):
    code = request.POST.get('coupon_code', '').strip().upper()
    cart = get_or_create_cart(request)
    try:
        coupon = Coupon.objects.get(code=code)
        if coupon.is_valid():
            if cart.subtotal >= coupon.min_order_value:
                request.session['coupon_code'] = code
                messages.success(request, f'Coupon "{code}" applied successfully!')
            else:
                messages.error(request, f'Minimum order value of ₹{coupon.min_order_value} required.')
        else:
            messages.error(request, 'This coupon is invalid or expired.')
    except Coupon.DoesNotExist:
        messages.error(request, 'Invalid coupon code.')
    return redirect('cart')


def remove_coupon_view(request):
    if 'coupon_code' in request.session:
        del request.session['coupon_code']
        messages.info(request, 'Coupon removed.')
    return redirect('cart')

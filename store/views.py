from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Avg, Count
from .models import Product, Category, Brand, Review, Wishlist
from .forms import ReviewForm, ProductSearchForm


def home_view(request):
    featured_products = Product.objects.filter(is_active=True, is_featured=True)[:8]
    new_arrivals = Product.objects.filter(is_active=True).order_by('-created_at')[:8]
    categories = Category.objects.filter(is_active=True, parent=None)[:6]
    on_sale = Product.objects.filter(is_active=True, discount_price__isnull=False)[:8]
    context = {
        'featured_products': featured_products,
        'new_arrivals': new_arrivals,
        'categories': categories,
        'on_sale': on_sale,
    }
    return render(request, 'store/home.html', context)


def product_list_view(request):
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.filter(is_active=True)
    brands = Brand.objects.filter(is_active=True)
    form = ProductSearchForm(request.GET)


    category_slug = request.GET.get('category')
    brand_slug = request.GET.get('brand')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    search_q = request.GET.get('q')
    sort = request.GET.get('sort', '-created_at')

    if category_slug:
        products = products.filter(category__slug=category_slug)
    if brand_slug:
        products = products.filter(brand__slug=brand_slug)
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    if search_q:
        products = products.filter(
            Q(name__icontains=search_q) |
            Q(description__icontains=search_q) |
            Q(category__name__icontains=search_q)
        )


    sort_options = {
        'price_asc': 'price',
        'price_desc': '-price',
        'name_asc': 'name',
        'newest': '-created_at',
        'popular': '-created_at',
    }
    products = products.order_by(sort_options.get(sort, '-created_at'))

    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'categories': categories,
        'brands': brands,
        'form': form,
        'total_count': products.count(),
        'current_sort': sort,
    }
    return render(request, 'store/product_list.html', context)


def product_detail_view(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    reviews = product.reviews.filter(is_approved=True).select_related('user')
    related_products = Product.objects.filter(
        category=product.category, is_active=True
    ).exclude(id=product.id)[:4]
    specs = product.specifications.all()
    gallery = product.images.all()


    user_review = None
    is_wishlisted = False
    if request.user.is_authenticated:
        user_review = reviews.filter(user=request.user).first()
        is_wishlisted = Wishlist.objects.filter(user=request.user, product=product).exists()


    if request.method == 'POST' and request.user.is_authenticated:
        if user_review:
            messages.warning(request, 'You have already reviewed this product.')
        else:
            form = ReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.product = product
                review.user = request.user

                from orders.models import OrderItem
                review.is_verified_purchase = OrderItem.objects.filter(
                    order__user=request.user, product=product
                ).exists()
                review.save()
                messages.success(request, 'Your review has been submitted!')
                return redirect('product_detail', slug=slug)
        form = ReviewForm(request.POST)
    else:
        form = ReviewForm()

    context = {
        'product': product,
        'reviews': reviews,
        'related_products': related_products,
        'specs': specs,
        'gallery': gallery,
        'review_form': form,
        'user_review': user_review,
        'is_wishlisted': is_wishlisted,
        'rating_range': range(1, 6),
    }
    return render(request, 'store/product_detail.html', context)


def category_products_view(request, slug):
    category = get_object_or_404(Category, slug=slug, is_active=True)
    products = Product.objects.filter(category=category, is_active=True)
    paginator = Paginator(products, 12)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'store/category_products.html', {
        'category': category,
        'page_obj': page_obj,
    })


@login_required
def toggle_wishlist_view(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    if not created:
        wishlist_item.delete()
        messages.info(request, f'"{product.name}" removed from wishlist.')
    else:
        messages.success(request, f'"{product.name}" added to wishlist!')
    next_url = request.META.get('HTTP_REFERER', 'home')
    return redirect(next_url)


@login_required
def wishlist_view(request):
    wishlist = Wishlist.objects.filter(user=request.user).select_related('product')
    return render(request, 'store/wishlist.html', {'wishlist': wishlist})


def search_view(request):
    q = request.GET.get('q', '')
    products = Product.objects.filter(
        Q(name__icontains=q) | Q(description__icontains=q),
        is_active=True
    ) if q else Product.objects.none()
    return render(request, 'store/search_results.html', {'products': products, 'query': q})

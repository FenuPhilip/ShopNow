from django.contrib import admin
from .models import Category, Brand, Product, ProductImage, ProductSpecification, Review, Wishlist


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductSpecInline(admin.TabularInline):
    model = ProductSpecification
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'is_active', 'created_at']
    list_filter = ['is_active', 'parent']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'discount_price', 'stock', 'is_active', 'is_featured']
    list_filter = ['is_active', 'is_featured', 'category', 'brand']
    search_fields = ['name', 'sku', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['price', 'stock', 'is_active', 'is_featured']
    inlines = [ProductImageInline, ProductSpecInline]
    readonly_fields = ['created_at', 'updated_at', 'sku']
    fieldsets = (
        ('Basic Info', {'fields': ('name', 'slug', 'sku', 'category', 'brand', 'short_description', 'description')}),
        ('Pricing & Stock', {'fields': ('price', 'discount_price', 'stock', 'weight')}),
        ('Media', {'fields': ('image',)}),
        ('Status', {'fields': ('is_active', 'is_featured')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'rating', 'is_approved', 'is_verified_purchase', 'created_at']
    list_filter = ['is_approved', 'is_verified_purchase', 'rating']
    list_editable = ['is_approved']
    search_fields = ['user__email', 'product__name', 'title']
    actions = ['approve_reviews', 'disapprove_reviews']

    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
    approve_reviews.short_description = "Approve selected reviews"

    def disapprove_reviews(self, request, queryset):
        queryset.update(is_approved=False)
    disapprove_reviews.short_description = "Disapprove selected reviews"

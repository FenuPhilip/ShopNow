
from django.core.management.base import BaseCommand
from django.utils import timezone
from store.models import Category, Brand, Product
from cart.models import Coupon
from datetime import timedelta


class Command(BaseCommand):
    help = 'Seed database with sample data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding categories...')
        categories_data = [
            ('Electronics', 'Phones, laptops, gadgets'),
            ('Fashion', 'Clothing, shoes, accessories'),
            ('Home & Living', 'Furniture, decor, kitchen'),
            ('Sports', 'Fitness, outdoor, sports gear'),
            ('Books', 'Fiction, non-fiction, textbooks'),
            ('Beauty', 'Skincare, makeup, fragrances'),
        ]
        categories = {}
        for name, desc in categories_data:
            cat, _ = Category.objects.get_or_create(name=name, defaults={'description': desc})
            categories[name] = cat

        self.stdout.write('Seeding brands...')
        for brand_name in ['Samsung', 'Apple', 'Nike', 'Zara', 'IKEA', 'Lakme']:
            Brand.objects.get_or_create(name=brand_name)

        self.stdout.write('Seeding products...')
        products_data = [
            ('iPhone 15 Pro', categories['Electronics'], 129999, 109999, 10, True),
            ('Samsung Galaxy S24', categories['Electronics'], 89999, 79999, 15, True),
            ('MacBook Air M2', categories['Electronics'], 114999, None, 8, True),
            ('Wireless Earbuds', categories['Electronics'], 4999, 3499, 50, False),
            ('Smart Watch', categories['Electronics'], 29999, 24999, 20, True),
            ('Men\'s Casual T-Shirt', categories['Fashion'], 999, 699, 100, False),
            ('Women\'s Jeans', categories['Fashion'], 2499, 1799, 60, False),
            ('Running Shoes', categories['Sports'], 5999, 4499, 40, True),
            ('Yoga Mat', categories['Sports'], 1299, 999, 80, False),
            ('Sofa 3-Seater', categories['Home & Living'], 34999, 27999, 5, True),
            ('LED Desk Lamp', categories['Home & Living'], 1499, None, 35, False),
            ('Python Programming', categories['Books'], 599, 449, 200, False),
            ('Face Moisturizer SPF50', categories['Beauty'], 799, 599, 120, False),
        ]
        for name, cat, price, disc, stock, featured in products_data:
            Product.objects.get_or_create(
                name=name,
                defaults={
                    'category': cat,
                    'description': f'{name} - Premium quality product. Best in class.',
                    'short_description': f'Top-rated {name} available at the best price.',
                    'price': price,
                    'discount_price': disc,
                    'stock': stock,
                    'is_featured': featured,
                    'is_active': True,
                }
            )

        self.stdout.write('Seeding coupons...')
        Coupon.objects.get_or_create(
            code='WELCOME10',
            defaults={
                'discount_type': 'percentage',
                'discount_value': 10,
                'min_order_value': 500,
                'is_active': True,
                'valid_from': timezone.now(),
                'valid_to': timezone.now() + timedelta(days=365),
            }
        )
        Coupon.objects.get_or_create(
            code='FLAT500',
            defaults={
                'discount_type': 'fixed',
                'discount_value': 500,
                'min_order_value': 2000,
                'is_active': True,
                'valid_from': timezone.now(),
                'valid_to': timezone.now() + timedelta(days=180),
            }
        )

        self.stdout.write(self.style.SUCCESS('✅ Sample data seeded successfully!'))
        self.stdout.write('   Coupons: WELCOME10 (10% off), FLAT500 (₹500 off above ₹2000)')

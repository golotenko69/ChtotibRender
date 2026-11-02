from django.core.management.base import BaseCommand

from apps.products.models import Category, Product


class Command(BaseCommand):
    help = "Creates a small set of demo categories/products for local development and manual testing."

    def handle(self, *args, **options):
        categories = [
            ("Фигурки", "figures"),
            ("Аксессуары", "accessories"),
            ("Инженерные детали", "engineering-parts"),
        ]
        cat_objs = {}
        for name, slug in categories:
            cat, _ = Category.objects.get_or_create(slug=slug, defaults={"name": name})
            cat_objs[slug] = cat

        products = [
            ("Фигурка дракона", "dragon-figure", "figures", 1490, "SKU-DRAGON-01", 12, True),
            ("Держатель для телефона", "phone-stand", "accessories", 590, "SKU-STAND-01", 30, True),
            ("Кронштейн крепежный", "mounting-bracket", "engineering-parts", 890, "SKU-BRACKET-01", 20, False),
            ("Органайзер настольный", "desk-organizer", "accessories", 1290, "SKU-ORG-01", 15, True),
        ]
        for name, slug, cat_slug, price, sku, stock, featured in products:
            Product.objects.get_or_create(
                slug=slug,
                defaults=dict(
                    name=name, category=cat_objs[cat_slug], price=price, sku=sku,
                    stock=stock, is_active=True, is_featured=featured,
                    short_description=f"{name} — готовое изделие 3D-печати.",
                ),
            )

        self.stdout.write(self.style.SUCCESS("Demo data created."))

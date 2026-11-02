"""Session-based cart. No user accounts involved: state lives entirely
in the anonymous Django session, keyed by product id -> quantity."""
from decimal import Decimal

from django.conf import settings

from apps.products.models import Product

CART_SESSION_KEY = getattr(settings, "CART_SESSION_ID", "cart")
MAX_ITEM_QUANTITY = 50


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(CART_SESSION_KEY)
        if cart is None:
            cart = self.session[CART_SESSION_KEY] = {}
        self.cart = cart

    def add(self, product: Product, quantity: int = 1, replace: bool = False):
        product_id = str(product.id)
        quantity = max(1, min(int(quantity), MAX_ITEM_QUANTITY))
        if product_id in self.cart and not replace:
            new_qty = self.cart[product_id]["quantity"] + quantity
        else:
            new_qty = quantity
        new_qty = min(new_qty, MAX_ITEM_QUANTITY)
        self.cart[product_id] = {"quantity": new_qty}
        self.save()

    def remove(self, product_id):
        product_id = str(product_id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def update(self, product_id, quantity):
        product_id = str(product_id)
        quantity = int(quantity)
        if quantity <= 0:
            self.remove(product_id)
            return
        quantity = min(quantity, MAX_ITEM_QUANTITY)
        if product_id in self.cart:
            self.cart[product_id]["quantity"] = quantity
            self.save()

    def clear(self):
        self.session[CART_SESSION_KEY] = {}
        self.save()

    def save(self):
        self.session[CART_SESSION_KEY] = self.cart
        self.session.modified = True

    def __len__(self):
        return sum(item["quantity"] for item in self.cart.values())

    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        products_map = {str(p.id): p for p in products}
        for product_id, item in self.cart.items():
            product = products_map.get(product_id)
            if not product:
                continue
            quantity = item["quantity"]
            yield {
                "product": product,
                "quantity": quantity,
                "subtotal": product.price * quantity,
            }

    def get_total_price(self) -> Decimal:
        return sum((entry["subtotal"] for entry in self), Decimal("0"))

    def is_empty(self):
        return len(self.cart) == 0

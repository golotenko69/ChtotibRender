from apps.core.contacts import shop_contacts as build_shop_contacts
from apps.orders.cart import Cart


def cart(request):
    return {"cart": Cart(request)}


def shop_contacts(request):
    return {"shop": build_shop_contacts()}

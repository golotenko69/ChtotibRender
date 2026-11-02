from django.http import HttpResponse
from django.shortcuts import render

from apps.products.models import Product


def home(request):
    featured_products = Product.objects.featured()[:8]
    context = {"featured_products": featured_products}
    return render(request, "core/home.html", context)


def about(request):
    return render(request, "core/about.html")


def contact(request):
    return render(request, "core/contact.html")


def robots_txt(request):
    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        "Disallow: /manage/",
        "Disallow: /orders/cart/",
        "Disallow: /request/",
        "",
        f"Sitemap: {request.scheme}://{request.get_host()}/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")

from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from .models import Category, Product

PAGE_SIZE = 12
SORT_OPTIONS = {
    "new": "-created_at",
    "price_asc": "price",
    "price_desc": "-price",
    "name": "name",
}


def catalog(request):
    products = Product.objects.active().select_related("category")

    query = request.GET.get("q", "").strip()
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query) | Q(sku__icontains=query)
        )

    category_slug = request.GET.get("category", "").strip()
    active_category = None
    if category_slug:
        active_category = get_object_or_404(Category, slug=category_slug, is_active=True)
        products = products.filter(category=active_category)

    sort = request.GET.get("sort", "new")
    products = products.order_by(SORT_OPTIONS.get(sort, "-created_at"))

    paginator = Paginator(products, PAGE_SIZE)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "page_obj": page_obj,
        "categories": Category.objects.filter(is_active=True),
        "active_category": active_category,
        "query": query,
        "sort": sort,
    }
    return render(request, "products/catalog.html", context)


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.active().select_related("category").prefetch_related("images"),
        slug=slug,
    )
    related = (
        Product.objects.active()
        .filter(category=product.category)
        .exclude(pk=product.pk)[:4]
    )
    return render(request, "products/product_detail.html", {"product": product, "related": related})

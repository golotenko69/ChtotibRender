from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from apps.core.emails import send_scanning_request_emails

from .forms import ScanningRequestForm
from .models import ScanningRequest, ScanningRequestImage


def scanning_request(request):
    if request.method == "POST":
        form = ScanningRequestForm(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():
                photos = form.cleaned_data.pop("photos", [])
                scan_request = form.save()
                ScanningRequestImage.objects.bulk_create([
                    ScanningRequestImage(request=scan_request, image=photo) for photo in photos
                ])
            send_scanning_request_emails(scan_request)
            return redirect("scanning:success", request_number=scan_request.request_number)
    else:
        form = ScanningRequestForm()

    return render(request, "scanning/form.html", {"form": form})


def success(request, request_number):
    scan_request = get_object_or_404(ScanningRequest, request_number=request_number)
    return render(request, "orders/success.html", {"object": scan_request, "kind": "3D-сканирование"})

from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from apps.core.emails import send_print_request_emails

from .forms import CustomPrintRequestForm
from .models import CustomPrintRequest, PrintRequestPhoto


def custom_print_request(request):
    if request.method == "POST":
        form = CustomPrintRequestForm(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():
                photos = form.cleaned_data.pop("photos", [])
                print_request = form.save()
                PrintRequestPhoto.objects.bulk_create([
                    PrintRequestPhoto(request=print_request, image=photo) for photo in photos
                ])
            send_print_request_emails(print_request)
            return redirect("print_requests:success", request_number=print_request.request_number)
    else:
        form = CustomPrintRequestForm()

    return render(request, "print_requests/form.html", {"form": form})


def success(request, request_number):
    print_request = get_object_or_404(CustomPrintRequest, request_number=request_number)
    return render(request, "orders/success.html", {"object": print_request, "kind": "печать модели"})

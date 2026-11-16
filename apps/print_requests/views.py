from django.db import transaction
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from apps.core.emails import send_print_request_emails
from apps.core.security import remember_submitted_request, submitted_in_this_session

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
            remember_submitted_request(request, print_request.request_number)
            send_print_request_emails(print_request)
            return redirect("print_requests:success", request_number=print_request.request_number)
    else:
        form = CustomPrintRequestForm()

    return render(request, "print_requests/form.html", {"form": form})


def success(request, request_number):
    if not submitted_in_this_session(request, request_number):
        raise Http404
    print_request = get_object_or_404(CustomPrintRequest, request_number=request_number)
    return render(request, "orders/success.html", {"object": print_request, "kind": "печать модели"})

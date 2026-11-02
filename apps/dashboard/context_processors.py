from apps.orders.models import OrderRequest
from apps.print_requests.models import CustomPrintRequest
from apps.scanning.models import ScanningRequest


def nav_counts(request):
    """New-request counts for the dashboard sidebar badges.

    Cheap enough to run on every dashboard request; skipped entirely for
    the public site and for anonymous/non-staff users.
    """
    if not request.path.startswith("/manage/"):
        return {}
    if not request.user.is_authenticated or not request.user.is_staff:
        return {}

    return {
        "nav_counts": {
            "orders": OrderRequest.objects.filter(status="NEW").count(),
            "print": CustomPrintRequest.objects.filter(status="NEW").count(),
            "scan": ScanningRequest.objects.filter(status="NEW").count(),
        }
    }

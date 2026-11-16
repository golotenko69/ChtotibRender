"""Small request-level security helpers shared by the public views and
the dashboard."""
from django.shortcuts import resolve_url
from django.utils.http import url_has_allowed_host_and_scheme

SUBMITTED_REQUESTS_SESSION_KEY = "submitted_requests"
MAX_REMEMBERED_REQUESTS = 20


def safe_redirect_target(request, candidate, fallback):
    """Return `candidate` only if it points back to this site; otherwise
    the resolved `fallback`. Guards every user-supplied `next`/Referer
    redirect against open-redirect phishing."""
    if candidate and url_has_allowed_host_and_scheme(
        candidate,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return candidate
    return resolve_url(fallback)


def remember_submitted_request(request, request_number):
    """Mark a request number as created by this browser session so its
    confirmation page (which shows the client's phone) can be opened
    only by the person who submitted it."""
    numbers = list(request.session.get(SUBMITTED_REQUESTS_SESSION_KEY, []))
    if request_number not in numbers:
        numbers.append(request_number)
    request.session[SUBMITTED_REQUESTS_SESSION_KEY] = numbers[-MAX_REMEMBERED_REQUESTS:]


def submitted_in_this_session(request, request_number):
    return request_number in request.session.get(SUBMITTED_REQUESTS_SESSION_KEY, [])

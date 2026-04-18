"""
security/views_and_decorators.py
=================================
Drop these helpers into your existing apps as needed.

Contents
--------
1. RBAC decorators  – @approved_partner_required, @admin_required
2. Mixin            – OwnerRequiredMixin
3. Private-file view – serve_verification_document()
4. Webhook validator – stripe_webhook()
"""

import hashlib
import hmac
import logging
import os

import stripe  # pip install stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponse
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# 1. RBAC DECORATORS
# ═══════════════════════════════════════════════════════════

def approved_partner_required(view_func):
    """
    Combines @login_required with a partner approval check.

    Usage:
        @approved_partner_required
        def my_partner_view(request):
            ...

    Why: The @login_required decorator alone only verifies authentication.
    We also need to confirm that the logged-in user is (a) a Partner and
    (b) has been approved by an admin before they can manage listings.
    """
    @login_required
    def _wrapped(request, *args, **kwargs):
        # 1. Does the user have a linked Partner profile at all?
        if not hasattr(request.user, 'partner'):
            messages.error(request, 'Accès réservé aux partenaires.')
            return redirect('core:home')

        # 2. Has the admin approved this partner?
        if not request.user.partner.is_approved:
            messages.warning(
                request,
                'Votre compte partenaire est en attente d'approbation.',
            )
            return redirect('partners:pending')

        return view_func(request, *args, **kwargs)

    return _wrapped


def admin_required(view_func):
    """
    Requires the user to be a superuser or to have role == 'admin'.

    Usage:
        @admin_required
        def admin_dashboard(request):
            ...
    """
    @login_required
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_admin_user():
            raise PermissionDenied  # returns HTTP 403
        return view_func(request, *args, **kwargs)

    return _wrapped


# ═══════════════════════════════════════════════════════════
# 2. OWNER MIXIN (Class-Based Views)
# ═══════════════════════════════════════════════════════════

class OwnerRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Restrict a CBV so that only the object's owner can access it.

    Usage:
        class PostUpdateView(OwnerRequiredMixin, UpdateView):
            model = Post
            owner_field = 'author'   # the field on the model that holds the owner
            ...

    How it works:
        test_func() is called by UserPassesTestMixin before dispatching the
        request. If it returns False, the user gets a 403 Forbidden response.
        We compare request.user against the field named in `owner_field` on
        the object being accessed.
    """
    owner_field = 'author'   # override in subclass if needed

    def test_func(self):
        obj = self.get_object()
        return getattr(obj, self.owner_field) == self.request.user


# ═══════════════════════════════════════════════════════════
# 3. PRIVATE-FILE SERVING WITH NGINX X-Accel-Redirect
# ═══════════════════════════════════════════════════════════

@login_required
def serve_verification_document(request, partner_pk):
    """
    Serves a partner's verification document only to the document owner or
    an admin.  Files live in PRIVATE_MEDIA_ROOT which is outside MEDIA_ROOT
    (the publicly accessible directory), so Nginx will not serve them directly.

    In production, set Nginx to handle the actual byte transfer once Django
    has performed the authorization check — this is the X-Accel-Redirect pattern.

    Nginx config needed in the server block:
        # Django passes X-Accel-Redirect: /private_docs/<path>
        location /private_docs/ {
            internal;                              # blocks direct browser access
            alias /srv/wanderly/private_media/;   # real path on disk
        }

    Django side (this view):
        response['X-Accel-Redirect'] = '/private_docs/' + relative_path

    Why X-Accel-Redirect?
        Without it, Django would read the file into memory and stream it back to
        the client, wasting Python worker time on I/O that Nginx does much more
        efficiently.  With X-Accel-Redirect, Django handles auth, then hands off
        the bytes to Nginx with a special internal redirect header.
    """
    from partners.models import Partner   # local import avoids circular deps

    try:
        partner = Partner.objects.get(pk=partner_pk)
    except Partner.DoesNotExist:
        raise Http404

    # Only the partner themselves or an admin may download the document.
    if request.user != partner.user and not request.user.is_admin_user():
        raise PermissionDenied

    if not partner.verification_document:
        raise Http404('No document on file.')

    # Build the relative path within the private media directory.
    doc_path = partner.verification_document.name  # e.g. "verifications/certficat_sdg.jpg"

    response = HttpResponse()

    # Tell Nginx to serve the file instead of Django streaming it.
    # The /private_docs/ prefix matches the Nginx `location` block above.
    response['X-Accel-Redirect'] = '/private_docs/' + doc_path

    # Suggest a download filename.
    filename = os.path.basename(doc_path)
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    # Clear Content-Type so Nginx will set it correctly from the file extension.
    del response['Content-Type']

    logger.info(
        'Verification document accessed: partner=%s, by=%s, ip=%s',
        partner_pk,
        request.user.username,
        request.META.get('REMOTE_ADDR'),
    )
    return response


# ═══════════════════════════════════════════════════════════
# 4. STRIPE WEBHOOK SIGNATURE VALIDATION
# ═══════════════════════════════════════════════════════════

@csrf_exempt          # Webhooks come from Stripe, not a browser form
@require_POST
def stripe_webhook(request):
    """
    Receives and validates incoming Stripe webhook events.

    Why validate the signature?
        Without validation, any attacker who knows your webhook URL could send
        fake "payment succeeded" events and trigger order fulfillment for free.
        Stripe signs every event with a HMAC-SHA256 signature using your
        endpoint's secret.  We verify this before trusting any data in the body.

    Configuration in settings_production.py:
        STRIPE_SECRET_KEY     = config('STRIPE_SECRET_KEY')
        STRIPE_WEBHOOK_SECRET = config('STRIPE_WEBHOOK_SECRET')

    Install:  pip install stripe
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')
    webhook_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError:
        # Invalid JSON body
        logger.warning('Stripe webhook: invalid payload')
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        # Signature mismatch — reject the request immediately
        logger.warning(
            'Stripe webhook: signature mismatch from IP=%s',
            request.META.get('REMOTE_ADDR'),
        )
        return HttpResponse(status=400)

    # ─── Handle specific event types ────────────────────────
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        _handle_successful_payment(session)

    elif event['type'] == 'payment_intent.payment_failed':
        intent = event['data']['object']
        logger.warning('Payment failed: %s', intent.get('id'))

    # Always return 200 so Stripe doesn't keep retrying.
    return HttpResponse(status=200)


def _handle_successful_payment(session):
    """Update booking status after a confirmed Stripe payment."""
    # Retrieve your internal booking ID from the session metadata.
    booking_id = session.get('metadata', {}).get('booking_id')
    if not booking_id:
        logger.error('Stripe session %s has no booking_id in metadata', session.get('id'))
        return

    from booking.models import Booking   # local import
    try:
        booking = Booking.objects.get(pk=booking_id)
        booking.status = 'confirmed'
        booking.stripe_payment_intent = session.get('payment_intent', '')
        booking.save(update_fields=['status', 'stripe_payment_intent'])
        logger.info('Booking %s confirmed via Stripe', booking_id)
    except Booking.DoesNotExist:
        logger.error('Booking %s not found after Stripe payment', booking_id)

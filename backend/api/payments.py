"""Payment gateways. Stripe implemented; UAE gateways stubbed with the
same interface so the booking flow never changes."""
from abc import ABC, abstractmethod
from decimal import Decimal

from django.conf import settings


class PaymentGateway(ABC):
    @abstractmethod
    def create_checkout(self, invoice, amount: Decimal, currency="AED") -> dict:
        """Return {'client_secret' | 'redirect_url', 'ref': gateway reference}."""

    @abstractmethod
    def verify_webhook(self, request) -> dict:
        """Validate a webhook and return {'ref', 'status', 'amount'}."""


class StripeGateway(PaymentGateway):
    def __init__(self):
        import stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY
        self.stripe = stripe

    def create_checkout(self, invoice, amount, currency="AED"):
        intent = self.stripe.PaymentIntent.create(
            amount=int(amount * 100),
            currency=currency.lower(),
            metadata={"invoice": invoice.number},
        )
        return {"client_secret": intent.client_secret, "ref": intent.id}

    def verify_webhook(self, request):
        event = self.stripe.Webhook.construct_event(
            request.body,
            request.headers.get("Stripe-Signature", ""),
            settings.STRIPE_WEBHOOK_SECRET,
        )
        obj = event.data.object
        return {
            "ref": obj.id,
            "status": "paid" if event.type == "payment_intent.succeeded" else event.type,
            "amount": Decimal(obj.amount) / 100,
        }


class TelrGateway(PaymentGateway):
    """https://telr.com — popular UAE gateway. Implement order create + IVP callback."""

    def create_checkout(self, invoice, amount, currency="AED"):
        raise NotImplementedError("Add Telr ivp/order API call here")

    def verify_webhook(self, request):
        raise NotImplementedError


class PayTabsGateway(PaymentGateway):
    def create_checkout(self, invoice, amount, currency="AED"):
        raise NotImplementedError("Add PayTabs payment-page API call here")

    def verify_webhook(self, request):
        raise NotImplementedError


class NetworkIntlGateway(PaymentGateway):
    def create_checkout(self, invoice, amount, currency="AED"):
        raise NotImplementedError("Add N-Genius hosted-payment-page call here")

    def verify_webhook(self, request):
        raise NotImplementedError


GATEWAYS = {
    "stripe": StripeGateway,
    "telr": TelrGateway,
    "paytabs": PayTabsGateway,
    "networkintl": NetworkIntlGateway,
}


def get_gateway() -> PaymentGateway:
    return GATEWAYS[settings.PAYMENT_GATEWAY]()

from django.db.models import Sum
from django.utils.crypto import get_random_string
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from . import models, notifications, pricing, serializers
from .payments import get_gateway
from .permissions import IsAdmin, IsOwnerRole


class UnitViewSet(viewsets.ModelViewSet):
    """Public search shows verified units only; owners manage their own."""
    serializer_class = serializers.UnitSerializer
    filterset_fields = ["emirate", "format", "illumination"]
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = models.Unit.objects.select_related("owner").prefetch_related("photos")
        user = self.request.user
        if user.is_authenticated and user.role == "owner":
            return qs.filter(owner__user=user)
        if user.is_authenticated and user.role == "admin":
            return qs
        qs = qs.filter(status=models.Unit.Status.VERIFIED)
        if max_price := self.request.query_params.get("max_price"):
            qs = qs.filter(price_monthly__lte=max_price)
        if min_traffic := self.request.query_params.get("min_traffic"):
            qs = qs.filter(daily_traffic__gte=min_traffic)
        return qs

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user.media_company)

    @action(detail=True, methods=["post"], permission_classes=[IsAdmin])
    def verify(self, request, pk=None):
        unit = self.get_object()
        unit.status = models.Unit.Status.VERIFIED
        unit.save(update_fields=["status"])
        return Response({"status": unit.status})


class CampaignViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.CampaignSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return models.Campaign.objects.filter(advertiser__user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(advertiser=self.request.user.advertiser)


class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = models.Booking.objects.select_related("unit", "campaign")
        if user.role == "owner":
            return qs.filter(unit__owner__user=user)
        if user.role == "admin":
            return qs
        return qs.filter(campaign__advertiser__user=user)

    def perform_create(self, serializer):
        unit = serializer.validated_data["unit"]
        start, end = serializer.validated_data["start"], serializer.validated_data["end"]
        booking = serializer.save(
            media_price=pricing.compute_media_price(unit, start, end),
            commission_pct=pricing.commission_pct_for(unit),
            vat_pct=pricing.vat_pct(),
        )
        notifications.notify_booking_requested(booking)

    @action(detail=True, methods=["post"], permission_classes=[IsOwnerRole])
    def decide(self, request, pk=None):
        """Owner accepts or rejects: {"accept": true}"""
        booking = self.get_object()
        accept = bool(request.data.get("accept"))
        booking.status = (models.Booking.Status.ACCEPTED if accept
                          else models.Booking.Status.REJECTED)
        booking.save(update_fields=["status"])
        return Response({"status": booking.status})

    @action(detail=True, methods=["post"])
    def proof(self, request, pk=None):
        ser = serializers.PlayProofSerializer(
            data={**request.data, "booking": pk})
        ser.is_valid(raise_exception=True)
        ser.save()
        booking = self.get_object()
        kinds = set(booking.proofs.values_list("kind", flat=True))
        if {"install", "display"} <= kinds:
            booking.status = models.Booking.Status.LIVE
            booking.save(update_fields=["status"])
        return Response(ser.data, status=status.HTTP_201_CREATED)


class CreativeViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.CreativeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == "admin":
            return models.Creative.objects.all()
        return models.Creative.objects.filter(
            booking__campaign__advertiser__user=user)

    @action(detail=True, methods=["post"], permission_classes=[IsAdmin])
    def review(self, request, pk=None):
        """{"approve": true} or {"approve": false, "note": "..."}"""
        creative = self.get_object()
        if request.data.get("approve"):
            creative.status = models.Creative.Status.APPROVED
        else:
            creative.status = models.Creative.Status.REJECTED
            creative.review_note = request.data.get("note", "")
        creative.save()
        return Response({"status": creative.status})


class CheckoutView(APIView):
    """POST {"booking": id, "mode": "deposit"|"full"} → payment session."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        from django.conf import settings
        booking = models.Booking.objects.get(
            pk=request.data["booking"],
            campaign__advertiser__user=request.user)
        invoice, _ = models.Invoice.objects.get_or_create(
            booking=booking,
            defaults={"number": "INV-" + get_random_string(8).upper(),
                      "amount": booking.total},
        )
        amount = (invoice.amount * settings.DEPOSIT_PCT / 100
                  if request.data.get("mode") == "deposit" else invoice.amount)
        session = get_gateway().create_checkout(invoice, amount)
        invoice.gateway_ref = session["ref"]
        invoice.save(update_fields=["gateway_ref"])
        return Response(session)


class SalesReportView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        qs = models.Booking.objects.exclude(
            status__in=["quote", "requested", "rejected", "cancelled"])
        by_emirate = (qs.values("unit__emirate")
                        .annotate(gross=Sum("media_price"))
                        .order_by("-gross"))
        return Response({
            "gross": qs.aggregate(v=Sum("media_price"))["v"] or 0,
            "by_emirate": list(by_emirate),
            "bookings": qs.count(),
        })

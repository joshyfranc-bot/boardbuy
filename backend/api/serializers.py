from rest_framework import serializers

from . import models


class UnitPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UnitPhoto
        fields = ["id", "image", "sort"]


class UnitSerializer(serializers.ModelSerializer):
    photos = UnitPhotoSerializer(many=True, read_only=True)
    owner_name = serializers.CharField(source="owner.name", read_only=True)
    lat = serializers.SerializerMethodField()
    lng = serializers.SerializerMethodField()

    class Meta:
        model = models.Unit
        fields = [
            "id", "name", "emirate", "area", "lat", "lng", "facing",
            "format", "illumination", "width_m", "height_m", "daily_traffic",
            "price_daily", "price_weekly", "price_monthly",
            "status", "owner_name", "photos",
        ]
        read_only_fields = ["status"]

    def get_lat(self, obj):
        return obj.location.y if obj.location else None

    def get_lng(self, obj):
        return obj.location.x if obj.location else None


class BookingSerializer(serializers.ModelSerializer):
    unit_name = serializers.CharField(source="unit.name", read_only=True)
    total = serializers.ReadOnlyField()
    owner_payout = serializers.ReadOnlyField()

    class Meta:
        model = models.Booking
        fields = [
            "id", "campaign", "unit", "unit_name", "start", "end",
            "media_price", "commission_pct", "vat_pct",
            "total", "owner_payout", "status", "created_at",
        ]
        read_only_fields = ["media_price", "commission_pct", "vat_pct", "status"]


class CampaignSerializer(serializers.ModelSerializer):
    bookings = BookingSerializer(many=True, read_only=True)

    class Meta:
        model = models.Campaign
        fields = ["id", "name", "start", "end", "bookings", "created_at"]


class CreativeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Creative
        fields = ["id", "booking", "file", "status", "review_note", "uploaded_at"]
        read_only_fields = ["status", "review_note"]


class PlayProofSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PlayProof
        fields = ["id", "booking", "kind", "image", "taken_at"]


class DisputeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Dispute
        fields = [
            "id", "booking", "reason", "claim_amount",
            "status", "resolution", "resolution_note", "created_at",
        ]
        read_only_fields = ["status", "resolution", "resolution_note"]

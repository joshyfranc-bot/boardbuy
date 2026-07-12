"""Core marketplace models. Unit.location is a PostGIS Point."""
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.gis.db import models as gis
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADVERTISER = "advertiser"
        OWNER = "owner"
        ADMIN = "admin"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.ADVERTISER)
    phone = models.CharField(max_length=32, blank=True)


class MediaCompany(models.Model):
    """A billboard owner (media company). Requires admin approval."""
    class Status(models.TextChoices):
        PENDING = "pending"
        APPROVED = "approved"
        REJECTED = "rejected"

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="media_company")
    name = models.CharField(max_length=200)
    trade_licence = models.CharField(max_length=64)
    trn = models.CharField("VAT TRN", max_length=32, blank=True)
    emirate = models.CharField(max_length=40)
    iban = models.CharField(max_length=40, blank=True)
    licence_doc = models.FileField(upload_to="licences/", blank=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING)
    commission_pct = models.DecimalField(  # per-owner override; null = platform default
        max_digits=5, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Advertiser(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending"
        APPROVED = "approved"
        REJECTED = "rejected"

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="advertiser")
    company_name = models.CharField(max_length=200)
    trn = models.CharField(max_length=32, blank=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.company_name


class Unit(models.Model):
    """A billboard. Verified by admin before appearing in the marketplace."""
    class Format(models.TextChoices):
        STATIC = "static", "Static Unipole"
        DIGITAL = "digital", "Digital Unipole"
        BRIDGE = "bridge", "Bridge Banner"
        MEGACOM = "megacom", "Megacom / Wallscape"
        HOARDING = "hoarding", "Hoarding"
        LAMPPOST = "lamppost", "Lamppost Series"

    class Illumination(models.TextChoices):
        FRONT = "front", "Front-lit"
        BACK = "back", "Back-lit"
        DIGITAL = "digital", "Digital (self-lit)"
        NONE = "none", "Non-illuminated"

    class Status(models.TextChoices):
        PENDING = "pending"
        VERIFIED = "verified"
        CHANGES = "changes_requested"
        REJECTED = "rejected"

    owner = models.ForeignKey(MediaCompany, on_delete=models.CASCADE, related_name="units")
    name = models.CharField(max_length=200)
    emirate = models.CharField(max_length=40, db_index=True)
    area = models.CharField(max_length=120)
    location = gis.PointField(geography=True)          # GPS — PostGIS point
    facing = models.CharField(max_length=80, blank=True)
    format = models.CharField(max_length=20, choices=Format.choices, db_index=True)
    illumination = models.CharField(max_length=12, choices=Illumination.choices)
    width_m = models.DecimalField(max_digits=6, decimal_places=2)
    height_m = models.DecimalField(max_digits=6, decimal_places=2)
    daily_traffic = models.PositiveIntegerField(default=0)
    price_daily = models.DecimalField(max_digits=10, decimal_places=2)
    price_weekly = models.DecimalField(max_digits=10, decimal_places=2)
    price_monthly = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    review_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class UnitPhoto(models.Model):
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name="photos")
    image = models.ImageField(upload_to="units/")
    sort = models.PositiveSmallIntegerField(default=0)


class AvailabilitySlot(models.Model):
    """Owner-managed availability; bookings lock overlapping ranges."""
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name="availability")
    start = models.DateField()
    end = models.DateField()
    is_blocked = models.BooleanField(default=False)

    class Meta:
        indexes = [models.Index(fields=["unit", "start", "end"])]


class Campaign(models.Model):
    advertiser = models.ForeignKey(Advertiser, on_delete=models.CASCADE, related_name="campaigns")
    name = models.CharField(max_length=200)
    start = models.DateField()
    end = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Booking(models.Model):
    """One unit within a campaign. Quote → booking → paid → live → completed."""
    class Status(models.TextChoices):
        QUOTE = "quote", "Quotation requested"
        REQUESTED = "requested", "Awaiting owner"
        ACCEPTED = "accepted"
        REJECTED = "rejected"
        DEPOSIT_PAID = "deposit_paid"
        PAID = "paid"
        INSTALLING = "installing"
        LIVE = "live"
        COMPLETED = "completed"
        CANCELLED = "cancelled"

    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name="bookings")
    unit = models.ForeignKey(Unit, on_delete=models.PROTECT, related_name="bookings")
    start = models.DateField()
    end = models.DateField()
    media_price = models.DecimalField(max_digits=12, decimal_places=2)
    commission_pct = models.DecimalField(max_digits=5, decimal_places=2)
    vat_pct = models.DecimalField(max_digits=5, decimal_places=2)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.REQUESTED)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total(self):
        return self.media_price * (1 + self.vat_pct / 100)

    @property
    def owner_payout(self):
        return self.media_price * (1 - self.commission_pct / 100)


class Creative(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "In review"
        APPROVED = "approved"
        REJECTED = "rejected"

    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="creatives")
    file = models.FileField(upload_to="creatives/")
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING)
    review_note = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)


class PlayProof(models.Model):
    class Kind(models.TextChoices):
        INSTALL = "install", "Installation photo"
        DISPLAY = "display", "Proof of display"

    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="proofs")
    kind = models.CharField(max_length=10, choices=Kind.choices)
    image = models.ImageField(upload_to="proofs/")
    taken_at = models.DateTimeField(auto_now_add=True)


class Invoice(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft"
        SENT = "sent"
        DEPOSIT_PAID = "deposit_paid"
        PAID = "paid"
        REFUNDED = "refunded"

    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name="invoice")
    number = models.CharField(max_length=24, unique=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    gateway = models.CharField(max_length=20, default="stripe")
    gateway_ref = models.CharField(max_length=120, blank=True)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.DRAFT)
    issued_at = models.DateTimeField(auto_now_add=True)


class Dispute(models.Model):
    class Status(models.TextChoices):
        OPEN = "open"
        RESOLVED = "resolved"

    class Resolution(models.TextChoices):
        FULL_REFUND = "full_refund"
        PARTIAL_REFUND = "partial_refund"
        DATE_CREDIT = "date_credit"
        DENIED = "denied"

    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="disputes")
    raised_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    reason = models.TextField()
    claim_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.OPEN)
    resolution = models.CharField(max_length=20, choices=Resolution.choices, blank=True)
    resolution_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


# =====================================================================
# Media formats & screen specifications
# =====================================================================

class MediaFormat(models.Model):
    """Admin-managed reference table for OOH formats (richer than Unit.format)."""
    code = models.SlugField(unique=True)                 # e.g. "digital-unipole"
    name = models.CharField(max_length=100)
    is_digital = models.BooleanField(default=False)
    requires_production = models.BooleanField(default=True)  # printing/installation
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class ScreenSpec(models.Model):
    """Technical specs for digital units (one per unit)."""
    unit = models.OneToOneField(Unit, on_delete=models.CASCADE, related_name="screen_spec")
    resolution_w = models.PositiveIntegerField(help_text="pixels")
    resolution_h = models.PositiveIntegerField(help_text="pixels")
    pixel_pitch_mm = models.DecimalField(max_digits=5, decimal_places=2)
    slot_seconds = models.PositiveSmallIntegerField(default=10)
    loop_seconds = models.PositiveSmallIntegerField(default=60)
    max_brightness_nits = models.PositiveIntegerField(default=5000)
    supported_files = models.CharField(max_length=120, default="jpg,png,mp4")

    @property
    def slots_per_loop(self):
        return self.loop_seconds // self.slot_seconds


# =====================================================================
# Quotations & contracts
# =====================================================================

class Quotation(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft"
        SENT = "sent"
        ACCEPTED = "accepted"
        EXPIRED = "expired"
        DECLINED = "declined"

    number = models.CharField(max_length=24, unique=True)
    advertiser = models.ForeignKey(Advertiser, on_delete=models.CASCADE, related_name="quotations")
    campaign = models.ForeignKey(Campaign, on_delete=models.SET_NULL, null=True, blank=True)
    prepared_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    vat = models.DecimalField(max_digits=12, decimal_places=2)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    valid_until = models.DateField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.DRAFT)
    pdf = models.FileField(upload_to="quotations/", blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class QuotationItem(models.Model):
    quotation = models.ForeignKey(Quotation, on_delete=models.CASCADE, related_name="items")
    unit = models.ForeignKey(Unit, on_delete=models.PROTECT)
    start = models.DateField()
    end = models.DateField()
    price = models.DecimalField(max_digits=12, decimal_places=2)


class Contract(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft"
        SENT = "sent"
        SIGNED = "signed"
        CANCELLED = "cancelled"

    number = models.CharField(max_length=24, unique=True)
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name="contract")
    file = models.FileField(upload_to="contracts/", blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.DRAFT)
    sent_at = models.DateTimeField(null=True, blank=True)
    signed_at = models.DateTimeField(null=True, blank=True)
    signed_by_name = models.CharField(max_length=120, blank=True)


# =====================================================================
# Payments (transaction ledger; Invoice holds the balance)
# =====================================================================

class Payment(models.Model):
    class Kind(models.TextChoices):
        DEPOSIT = "deposit"
        BALANCE = "balance"
        FULL = "full"
        REFUND = "refund"
        PAYOUT = "payout"          # transfer to media owner

    class Status(models.TextChoices):
        PENDING = "pending"
        SUCCEEDED = "succeeded"
        FAILED = "failed"

    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="payments")
    kind = models.CharField(max_length=10, choices=Kind.choices)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="AED")
    gateway = models.CharField(max_length=20, default="stripe")
    gateway_ref = models.CharField(max_length=120, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


# =====================================================================
# Impressions & campaign reports
# =====================================================================

class ImpressionRecord(models.Model):
    """Daily audience estimate per booking (traffic counts, Geopath-style data,
    or camera/sensor feeds for digital units)."""
    class Source(models.TextChoices):
        TRAFFIC_MODEL = "traffic_model", "Modelled from traffic counts"
        SENSOR = "sensor", "Camera / sensor"
        PROVIDER = "provider", "Third-party data provider"

    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="impressions")
    date = models.DateField()
    impressions = models.PositiveIntegerField()
    plays = models.PositiveIntegerField(null=True, blank=True)  # digital: ad plays
    source = models.CharField(max_length=20, choices=Source.choices,
                              default=Source.TRAFFIC_MODEL)

    class Meta:
        unique_together = [("booking", "date", "source")]


class CampaignReport(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name="reports")
    period_start = models.DateField()
    period_end = models.DateField()
    total_impressions = models.BigIntegerField(default=0)
    total_plays = models.BigIntegerField(null=True, blank=True)
    total_spend = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    pdf = models.FileField(upload_to="reports/", blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)


# =====================================================================
# Reviews, notifications & support
# =====================================================================

class Review(models.Model):
    """Advertiser rates the unit/owner after campaign completion."""
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name="review")
    rating = models.PositiveSmallIntegerField()          # 1–5
    comment = models.TextField(blank=True)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Notification(models.Model):
    class Channel(models.TextChoices):
        IN_APP = "in_app"
        EMAIL = "email"
        WHATSAPP = "whatsapp"
        SMS = "sms"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name="notifications")
    channel = models.CharField(max_length=10, choices=Channel.choices,
                               default=Channel.IN_APP)
    title = models.CharField(max_length=200)
    body = models.TextField(blank=True)
    link = models.CharField(max_length=200, blank=True)   # deep link into the app
    is_read = models.BooleanField(default=False)
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-sent_at"]


class SupportTicket(models.Model):
    class Status(models.TextChoices):
        OPEN = "open"
        PENDING = "pending", "Awaiting user"
        CLOSED = "closed"

    class Priority(models.TextChoices):
        LOW = "low"
        NORMAL = "normal"
        HIGH = "high"

    number = models.CharField(max_length=16, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name="tickets")
    topic = models.CharField(max_length=60, default="general")
    subject = models.CharField(max_length=200)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.OPEN)
    priority = models.CharField(max_length=10, choices=Priority.choices,
                                default=Priority.NORMAL)
    booking = models.ForeignKey(Booking, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class TicketMessage(models.Model):
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE,
                               related_name="messages")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    body = models.TextField()
    attachment = models.FileField(upload_to="tickets/", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

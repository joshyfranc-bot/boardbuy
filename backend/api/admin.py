from django.contrib import admin

from . import models

for m in [
    models.User, models.MediaCompany, models.Advertiser,
    models.Unit, models.UnitPhoto, models.AvailabilitySlot,
    models.MediaFormat, models.ScreenSpec,
    models.Campaign, models.Booking,
    models.Quotation, models.QuotationItem, models.Contract,
    models.Creative, models.PlayProof,
    models.Invoice, models.Payment,
    models.ImpressionRecord, models.CampaignReport,
    models.Review, models.Notification,
    models.SupportTicket, models.TicketMessage,
    models.Dispute,
]:
    admin.site.register(m)

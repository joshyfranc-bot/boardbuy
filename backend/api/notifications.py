"""Email (SendGrid) + WhatsApp Business API notifications.
Both fail soft in dev when keys are missing."""
import logging
import os

import requests

log = logging.getLogger(__name__)


def send_email(to: str, subject: str, html: str):
    key = os.getenv("SENDGRID_API_KEY")
    if not key:
        log.info("[dev email] to=%s subject=%s", to, subject)
        return
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail
    SendGridAPIClient(key).send(
        Mail(from_email="no-reply@boardbuy.ae", to_emails=to,
             subject=subject, html_content=html))


def send_whatsapp(phone: str, text: str):
    token, phone_id = os.getenv("WHATSAPP_TOKEN"), os.getenv("WHATSAPP_PHONE_ID")
    if not token:
        log.info("[dev whatsapp] to=%s text=%s", phone, text)
        return
    requests.post(
        f"https://graph.facebook.com/v19.0/{phone_id}/messages",
        headers={"Authorization": f"Bearer {token}"},
        json={"messaging_product": "whatsapp", "to": phone,
              "type": "text", "text": {"body": text}},
        timeout=15,
    )


def notify_booking_requested(booking):
    owner = booking.unit.owner
    send_email(owner.user.email, "New booking request",
               f"<p>{booking.campaign.advertiser.company_name} requested "
               f"<b>{booking.unit.name}</b> {booking.start} → {booking.end}.</p>")
    if owner.user.phone:
        send_whatsapp(owner.user.phone,
                      f"BoardBuy: new booking request for {booking.unit.name}")

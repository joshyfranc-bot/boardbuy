"""Seed sample UAE inventory: manage.py seed_demo"""
from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand

from api import models

UNITS = [
    ("SZR — Trade Centre Digital", "Dubai", "Sheikh Zayed Road", 55.2870, 25.2252, "digital", 14, 48, 280000, 13500, 81000, 380000),
    ("Downtown Burj Vista Megacom", "Dubai", "Downtown Dubai", 55.2744, 25.1972, "megacom", 60, 30, 180000, 16000, 96000, 450000),
    ("Corniche Rd Digital", "Abu Dhabi", "Corniche", 54.3552, 24.4764, "digital", 12, 36, 140000, 7800, 47000, 220000),
    ("Al Wahda Bridge Banner", "Sharjah", "Al Wahda Road", 55.3924, 25.3325, "bridge", 28, 4, 150000, 2300, 14000, 65000),
    ("Ajman Corniche Static", "Ajman", "Ajman Corniche", 55.4370, 25.4136, "static", 12, 36, 55000, 1350, 8100, 38000),
]


class Command(BaseCommand):
    help = "Load demo media company + units"

    def handle(self, *args, **opts):
        user, _ = models.User.objects.get_or_create(
            username="demo_owner", defaults={"role": "owner", "email": "owner@demo.ae"})
        co, _ = models.MediaCompany.objects.get_or_create(
            user=user, defaults={
                "name": "Falcon Outdoor Media LLC", "trade_licence": "CN-1234567",
                "emirate": "Dubai", "status": "approved"})
        for (name, em, area, lng, lat, fmt, w, h, tr, pd, pw, pm) in UNITS:
            models.Unit.objects.get_or_create(
                owner=co, name=name, defaults={
                    "emirate": em, "area": area, "location": Point(lng, lat),
                    "format": fmt, "illumination": "front",
                    "width_m": w, "height_m": h, "daily_traffic": tr,
                    "price_daily": pd, "price_weekly": pw, "price_monthly": pm,
                    "status": "verified"})
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(UNITS)} units"))

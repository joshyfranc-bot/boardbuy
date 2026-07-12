from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("units", views.UnitViewSet, basename="unit")
router.register("campaigns", views.CampaignViewSet, basename="campaign")
router.register("bookings", views.BookingViewSet, basename="booking")
router.register("creatives", views.CreativeViewSet, basename="creative")

urlpatterns = [
    path("", include(router.urls)),
    path("payments/checkout/", views.CheckoutView.as_view()),
    path("reports/sales/", views.SalesReportView.as_view()),
]

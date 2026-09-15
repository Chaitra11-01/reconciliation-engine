from django.urls import path

from .views import discrepancies, tenants


urlpatterns = [
    path("discrepancies/", discrepancies, name="discrepancies"),
    path("tenants/", tenants, name="tenants"),
]
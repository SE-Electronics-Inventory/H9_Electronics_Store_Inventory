"""
Reports URL Configuration (FR-10, FR-11)
"""
from django.urls import path
from . import views

app_name = "reports"

urlpatterns = [
    path("", views.report_list, name="report_list"),
    path("dashboard/", views.dashboard, name="dashboard"),
]

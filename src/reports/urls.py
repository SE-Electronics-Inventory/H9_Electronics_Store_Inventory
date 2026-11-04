"""
Reports URL Configuration (FR-10, FR-11: Generate Inventory Reports)
"""
from django.urls import path
from . import views

app_name = "reports"

urlpatterns = [
    path("", views.report_list, name="report_list"),
    path("export/", views.export_report_csv, name="export_csv"),
    path("dashboard/", views.dashboard, name="dashboard"),
]

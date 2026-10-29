"""
Inventory URL Configuration (FR-03 to FR-09, FR-12, FR-13)
"""
from django.urls import path
from . import views

app_name = "inventory"

urlpatterns = [
    path("", views.component_list, name="list"),
    path("add/", views.component_add, name="add"),
    path("<int:pk>/edit/", views.component_edit, name="edit"),
    path("<int:pk>/delete/", views.component_delete, name="delete"),
    path("low-stock/", views.low_stock_list, name="low_stock"),
]

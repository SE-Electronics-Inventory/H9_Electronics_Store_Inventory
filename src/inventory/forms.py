from django import forms

from .models import Component


class ComponentForm(forms.ModelForm):
    """Validate component data before it reaches the database."""

    class Meta:
        model = Component
        fields = [
            "component_id",
            "name",
            "category",
            "description",
            "price",
            "quantity",
            "minimum_stock",
            "is_active",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }

    def clean_component_id(self):
        component_id = self.cleaned_data["component_id"].strip()
        if not component_id:
            raise forms.ValidationError("Component ID is required.")
        return component_id

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if not name:
            raise forms.ValidationError("Component name is required.")
        return name

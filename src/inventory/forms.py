from django import forms

from .models import Component


class ComponentForm(forms.ModelForm):
    """Validated form for creating an inventory component."""

    class Meta:
        model = Component
        fields = (
            "component_id",
            "name",
            "category",
            "description",
            "price",
            "quantity",
            "minimum_stock",
        )
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "price": forms.NumberInput(attrs={"min": "0", "step": "0.01"}),
            "quantity": forms.NumberInput(attrs={"min": "0", "step": "1"}),
            "minimum_stock": forms.NumberInput(attrs={"min": "0", "step": "1"}),
        }

from decimal import Decimal

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0001_initial"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="component",
            constraint=models.CheckConstraint(
                condition=models.Q(price__gte=Decimal("0.00")),
                name="component_price_non_negative",
            ),
        ),
        migrations.AddConstraint(
            model_name="component",
            constraint=models.CheckConstraint(
                condition=models.Q(quantity__gte=0),
                name="component_quantity_non_negative",
            ),
        ),
        migrations.AddConstraint(
            model_name="component",
            constraint=models.CheckConstraint(
                condition=models.Q(minimum_stock__gte=0),
                name="component_minimum_stock_non_negative",
            ),
        ),
    ]

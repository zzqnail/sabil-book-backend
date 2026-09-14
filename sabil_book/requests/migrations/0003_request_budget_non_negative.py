from django.core.validators import MinValueValidator
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):
    dependencies = [
        ("requests", "0002_rename_request_table"),
    ]

    operations = [
        migrations.AlterField(
            model_name="request",
            name="budget",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                max_digits=10,
                null=True,
                validators=[MinValueValidator(0)],
                verbose_name="Request Budget",
            ),
        ),
        migrations.AddConstraint(
            model_name="request",
            constraint=models.CheckConstraint(
                condition=models.Q(budget__gte=0) | models.Q(budget__isnull=True),
                name="request_budget_non_negative",
            ),
        ),
    ]

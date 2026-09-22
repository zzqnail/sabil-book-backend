import django.db.models.deletion
from django.conf import settings
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("users", "0005_request_moderation_workflow"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.CreateModel(
                    name="Request",
                    fields=[
                        (
                            "id",
                            models.BigAutoField(
                                auto_created=True,
                                primary_key=True,
                                serialize=False,
                                verbose_name="ID",
                            ),
                        ),
                        (
                            "category",
                            models.CharField(
                                choices=[
                                    ("research_brief", "Research brief"),
                                    (
                                        "professional_template",
                                        "Professional template / SOP",
                                    ),
                                    (
                                        "certification_material",
                                        "Certification material",
                                    ),
                                ],
                                max_length=32,
                                verbose_name="Request Category",
                            ),
                        ),
                        (
                            "title",
                            models.CharField(max_length=255, verbose_name="title"),
                        ),
                        (
                            "description",
                            models.TextField(verbose_name="description"),
                        ),
                        (
                            "budget",
                            models.DecimalField(
                                blank=True,
                                decimal_places=2,
                                max_digits=10,
                                null=True,
                                verbose_name="Request Budget",
                            ),
                        ),
                        (
                            "status",
                            models.CharField(
                                choices=[
                                    ("draft", "Draft"),
                                    ("manual_review", "Manual review"),
                                    ("published", "Published"),
                                    ("rejected", "Rejected"),
                                    ("closed", "Closed"),
                                ],
                                default="draft",
                                max_length=32,
                                verbose_name="Request Status",
                            ),
                        ),
                        (
                            "moderation_flags",
                            models.JSONField(
                                blank=True,
                                default=list,
                                verbose_name="moderation flags",
                            ),
                        ),
                        (
                            "rejection_reason",
                            models.TextField(
                                blank=True,
                                verbose_name="rejection reason",
                            ),
                        ),
                        (
                            "created_at",
                            models.DateTimeField(
                                auto_now_add=True,
                                verbose_name="created at",
                            ),
                        ),
                        (
                            "updated_at",
                            models.DateTimeField(
                                auto_now=True,
                                verbose_name="updated at",
                            ),
                        ),
                        (
                            "published_at",
                            models.DateTimeField(
                                blank=True,
                                null=True,
                                verbose_name="published at",
                            ),
                        ),
                        (
                            "closed_at",
                            models.DateTimeField(
                                blank=True,
                                null=True,
                                verbose_name="closed at",
                            ),
                        ),
                        (
                            "customer",
                            models.ForeignKey(
                                on_delete=django.db.models.deletion.CASCADE,
                                related_name="material_requests",
                                to=settings.AUTH_USER_MODEL,
                                verbose_name="user",
                            ),
                        ),
                    ],
                    options={
                        "db_table": "users_request",
                        "ordering": ["-created_at"],
                    },
                ),
            ],
        ),
    ]

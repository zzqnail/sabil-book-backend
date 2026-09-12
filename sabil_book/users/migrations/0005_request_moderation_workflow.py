import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations
from django.db import models


def normalize_request_values(apps, schema_editor):
    Request = apps.get_model("users", "Request")
    category_map = {
        "document": "professional_template",
        "course": "certification_material",
        "book": "research_brief",
        "journal": "research_brief",
        "article": "research_brief",
        "other": "research_brief",
    }
    status_map = {
        "open": "published",
        "in_progress": "published",
        "fulfilled": "closed",
        "cancelled": "closed",
        "expired": "closed",
    }
    for old_value, new_value in category_map.items():
        Request.objects.filter(category=old_value).update(category=new_value)
    for old_value, new_value in status_map.items():
        Request.objects.filter(status=old_value).update(status=new_value)
    Request.objects.filter(status="published", published_at__isnull=True).update(
        published_at=models.F("updated_at"),
    )
    Request.objects.filter(status="closed", closed_at__isnull=True).update(
        closed_at=models.F("updated_at"),
    )


def reverse_request_values(apps, schema_editor):
    Request = apps.get_model("users", "Request")
    category_map = {
        "research_brief": "book",
        "professional_template": "document",
        "certification_material": "course",
    }
    status_map = {
        "manual_review": "draft",
        "published": "open",
        "rejected": "draft",
        "closed": "fulfilled",
    }
    for old_value, new_value in category_map.items():
        Request.objects.filter(category=old_value).update(category=new_value)
    for old_value, new_value in status_map.items():
        Request.objects.filter(status=old_value).update(status=new_value)


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0004_alter_providerprofile_user_alter_request_budget"),
    ]

    operations = [
        migrations.AddField(
            model_name="request",
            name="closed_at",
            field=models.DateTimeField(blank=True, null=True, verbose_name="closed at"),
        ),
        migrations.AddField(
            model_name="request",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True,
                default=django.utils.timezone.now,
                verbose_name="created at",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="request",
            name="description",
            field=models.TextField(default="", verbose_name="description"),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="request",
            name="moderation_flags",
            field=models.JSONField(
                blank=True,
                default=list,
                verbose_name="moderation flags",
            ),
        ),
        migrations.AddField(
            model_name="request",
            name="published_at",
            field=models.DateTimeField(
                blank=True,
                null=True,
                verbose_name="published at",
            ),
        ),
        migrations.AddField(
            model_name="request",
            name="rejection_reason",
            field=models.TextField(blank=True, verbose_name="rejection reason"),
        ),
        migrations.AddField(
            model_name="request",
            name="title",
            field=models.CharField(default="", max_length=255, verbose_name="title"),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="request",
            name="updated_at",
            field=models.DateTimeField(
                auto_now=True,
                default=django.utils.timezone.now,
                verbose_name="updated at",
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="request",
            name="category",
            field=models.CharField(
                choices=[
                    ("research_brief", "Research brief"),
                    ("professional_template", "Professional template / SOP"),
                    ("certification_material", "Certification material"),
                ],
                max_length=32,
                verbose_name="Request Category",
            ),
        ),
        migrations.AlterField(
            model_name="request",
            name="customer",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="material_requests",
                to=settings.AUTH_USER_MODEL,
                verbose_name="user",
            ),
        ),
        migrations.AlterField(
            model_name="request",
            name="status",
            field=models.CharField(
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
        migrations.RunPython(normalize_request_values, reverse_request_values),
        migrations.AlterModelOptions(
            name="request",
            options={"ordering": ["-created_at"]},
        ),
    ]

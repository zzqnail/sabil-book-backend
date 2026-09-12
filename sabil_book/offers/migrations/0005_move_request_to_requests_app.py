import django.db.models.deletion
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):
    dependencies = [
        ("offers", "0004_alter_attachment_order_alter_message_offer_and_more"),
        ("requests", "0001_move_request_from_users"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.AlterField(
                    model_name="offer",
                    name="request",
                    field=models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="offers",
                        to="requests.request",
                        verbose_name="request",
                    ),
                ),
            ],
        ),
    ]

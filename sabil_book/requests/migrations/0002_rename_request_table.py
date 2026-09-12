from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0006_move_request_to_requests_app"),
        ("requests", "0001_move_request_from_users"),
    ]

    operations = [
        migrations.AlterModelTable(
            name="request",
            table=None,
        ),
    ]

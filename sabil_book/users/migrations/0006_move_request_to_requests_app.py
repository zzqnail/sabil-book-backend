from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("offers", "0005_move_request_to_requests_app"),
        ("users", "0005_request_moderation_workflow"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[migrations.DeleteModel(name="Request")],
        ),
    ]

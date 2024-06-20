# Generated by Django 5.0.6 on 2024-06-20 10:36

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0007_alter_useractivity_created_at"),
    ]

    operations = [
        migrations.AlterField(
            model_name="useractivity",
            name="followed_username",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="followed_user",
                to=settings.AUTH_USER_MODEL,
                to_field="username",
            ),
        ),
        migrations.AlterField(
            model_name="useractivity",
            name="review_id",
            field=models.UUIDField(blank=True, null=True),
        ),
    ]

# Generated by Django 5.0.6 on 2024-06-05 11:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0006_remove_useractivity_object_remove_useractivity_user_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="useractivity",
            name="movie_tmdb_id",
            field=models.IntegerField(blank=True, null=True),
        ),
    ]

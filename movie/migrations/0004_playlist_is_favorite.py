# Generated by Django 5.0.6 on 2024-06-01 18:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movie', '0003_alter_movie_id_alter_playlist_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='playlist',
            name='is_favorite',
            field=models.BooleanField(default=False),
        ),
    ]
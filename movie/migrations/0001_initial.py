# Generated by Django 5.0.6 on 2024-06-02 17:04

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Movie',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('tmdb_id', models.IntegerField()),
                ('title', models.CharField(max_length=255)),
                ('poster_url', models.URLField()),
                ('description', models.TextField()),
                ('director', models.CharField(max_length=255)),
                ('release_date', models.DateField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('rating', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='Playlist',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('is_favorite', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='playlists', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PlaylistMovie',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('added_at', models.DateTimeField(auto_now_add=True)),
                ('movie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='movie.movie')),
                ('playlist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='movie.playlist')),
            ],
            options={
                'unique_together': {('playlist', 'movie')},
            },
        ),
        migrations.AddField(
            model_name='playlist',
            name='movies',
            field=models.ManyToManyField(through='movie.PlaylistMovie', to='movie.movie'),
        ),
    ]
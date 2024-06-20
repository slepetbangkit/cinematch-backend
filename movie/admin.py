from django.contrib import admin
from .models import Movie, Review, Playlist, BlendedPlaylist

# Register your models here.
admin.site.register((Movie, Review, Playlist, BlendedPlaylist))

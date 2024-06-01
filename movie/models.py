from django.db import models
import uuid

# add user models
from user.models import CustomUser




# Create your models here.
class Movie(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    director = models.CharField(max_length=255)
    release_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    rating = models.FloatField()

    def __str__(self):
        return self.title

class Playlist(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    is_favorite = models.BooleanField(default=False) # favorite playlist or custom playlist
    user = models.ForeignKey(CustomUser, related_name='playlists', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    movies = models.ManyToManyField(Movie, through='PlaylistMovie')

    def __str__(self):
        return self.title

class PlaylistMovie(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('playlist', 'movie')
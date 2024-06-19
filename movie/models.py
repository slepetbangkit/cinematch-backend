from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
import uuid

# add user models
from user.models import CustomUser


# Create your models here.
class Movie(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tmdb_id = models.IntegerField()
    title = models.CharField(max_length=255)
    poster_url = models.URLField()
    description = models.TextField()
    director = models.CharField(max_length=255)
    release_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    rating = models.FloatField()
    review_count = models.IntegerField(default=0)

    def __str__(self):
        return self.title


class Playlist(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(default="")
    is_favorite = models.BooleanField(default=False) # favorite playlist or custom playlist
    user = models.ForeignKey(CustomUser, related_name='playlist_user', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    movies = models.ManyToManyField(Movie, through='PlaylistMovie')

    class Meta:
        ordering = ["-is_favorite", "-created_at"]

    def __str__(self):
        return self.title


class PlaylistMovie(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('playlist', 'movie')


class Review(models.Model):
    POSITIVE = "POSITIVE"
    NEUTRAL = "NEUTRAL"
    NEGATIVE = "NEGATIVE"

    SENTIMENT_TYPES = [
        (POSITIVE, "POSITIVE"),
        (NEUTRAL, "NEUTRAL"),
        (NEGATIVE, "NEGATIVE"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, related_name='reviewer', on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    description = models.CharField(max_length=280)
    rating = models.FloatField(validators=[
        MinValueValidator(0.0),
        MaxValueValidator(1.0)
    ])
    sentiment = models.CharField(max_length=10, blank=True, choices=SENTIMENT_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [["user", "movie"]]
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        percentage = self.rating * 100
        if 60 <= percentage <= 100:
            self.sentiment = "positive"
        elif 40 <= percentage < 60:
            self.sentiment = "neutral"
        else:
            self.sentiment = "negative"
        super(Review, self).save(*args, **kwargs)

class BlendedPlaylist(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    second_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('playlist', 'second_user')
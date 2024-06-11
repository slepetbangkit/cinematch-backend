import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bio = models.CharField(max_length=255, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True)
    follower_count = models.IntegerField(default=0)
    following_count = models.IntegerField(default=0)


class UserFollowing(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
            CustomUser,
            on_delete=models.CASCADE,
            related_name='follower')
    following_user = models.ForeignKey(
            CustomUser,
            on_delete=models.CASCADE,
            related_name='following')
    created_at = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = [["user", "following_user"]]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} follows {self.following_user}"


class UserActivity(models.Model):
    LIKED_MOVIE = "LIKED_MOVIE"
    REVIEWED_MOVIE = "REVIEWED_MOVIE"
    FOLLOWED_USER = "FOLLOWED_USER"
    ADDED_MOVIE_TO_PLAYLIST = "ADDED_MOVIE_TO_PLAYLIST"

    ACTIVITY_TYPES = [
        (LIKED_MOVIE, "LIKED_MOVIE"),
        (REVIEWED_MOVIE, "REVIEWED_MOVIE"),
        (FOLLOWED_USER, "FOLLOWED_USER"),
        (ADDED_MOVIE_TO_PLAYLIST, "ADDED_MOVIE_TO_PLAYLIST"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    description = models.CharField(max_length=150)
    username = models.ForeignKey(
            CustomUser,
            on_delete=models.CASCADE,
            to_field='username',
            related_name='user',
            null=True)
    followed_username = models.ForeignKey(
            CustomUser,
            on_delete=models.CASCADE,
            to_field='username',
            related_name='followed_user',
            null=True)
    movie_tmdb_id = models.IntegerField(blank=True, null=True)
    type = models.CharField(max_length=100, choices=ACTIVITY_TYPES)
    created_at = models.DateField(auto_now_add=True)

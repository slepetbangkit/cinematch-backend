import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bio = models.CharField(max_length=255, blank=True)
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
        return f"{self.user_id} follows {self.following_user_id}"

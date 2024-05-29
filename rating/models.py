from django.db import models

# Create your models here.
class Review(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    movie_id = models.CharField(max_length=255)
    rating = models.FloatField()
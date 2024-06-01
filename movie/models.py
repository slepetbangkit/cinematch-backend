from django.db import models

# Create your models here.
class Movie(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    release_date = models.DateField()
    genre = models.CharField(max_length=255)

    def __str__(self):
        return self.title

# class Playlist(models.Model):
#     title = models.CharField(max_length=255)
#     description = models.TextField()
#     user = models.ForeignKey(CustomUser, related_name='playlists', on_delete=models.CASCADE)
#     created_at = models.DateTimeField(auto_now_add=True)
#     movies = models.ManyToManyField(Movie, through='PlaylistMovie')

#     def __str__(self):
#         return self.title

# class PlaylistMovie(models.Model):
#     playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
#     movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
#     added_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         unique_together = ('playlist', 'movie')
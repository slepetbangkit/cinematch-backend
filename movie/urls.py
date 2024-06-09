from django.urls import path
from .views import (
    MovieView,
    MovieDetailTMDBView,
    PlaylistView,
    PlaylistDetailView
)

urlpatterns = [
    path('', MovieView.as_view(), name='movies'),
    path('details/<int:pk>/', MovieDetailTMDBView.as_view(), name='movie-tmdb'),
    path('playlists/', PlaylistView.as_view(), name='playlist'),
    path('playlists/<uuid:pk>/', PlaylistDetailView.as_view(), name='playlist-edit'),
]

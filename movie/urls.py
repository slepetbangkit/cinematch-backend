from django.urls import path
from .views import (
    MovieView,
    MovieDetailTMDBView,
    PlaylistView,
    PlaylistDetailView,
    ReviewView,
    getReviewDetailById,
    getHome,
)

urlpatterns = [
    path('', MovieView.as_view(), name='movies'),
    path('details/<int:pk>/', MovieDetailTMDBView.as_view(), name='movie-tmdb'),
    path('details/<int:pk>/review/', ReviewView.as_view(), name='review-movie-by-tmdb-id'),
    path('review/<uuid:pk>/', getReviewDetailById, name='review-by-id'),
    path('playlists/', PlaylistView.as_view(), name='playlist'),
    path('playlists/<uuid:pk>/', PlaylistDetailView.as_view(), name='playlist-edit'),
    path('home/', getHome, name='home'),
]

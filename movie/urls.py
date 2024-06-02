from django.urls import path
from .views import (
    MovieView,
    PlaylistView,
    PlaylistDetailView
)

urlpatterns = [
    path('', MovieView.as_view(), name='movies'),
    path('<str:query>', MovieView.as_view(), name='movies'),
    path('playlists/', PlaylistView.as_view(), name='playlist'),
    path('playlists/<uuid:pk>/', PlaylistDetailView.as_view(), name='playlist-edit')

]

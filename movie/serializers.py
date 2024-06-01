from rest_framework.serializers import (
        ModelSerializer,
        ReadOnlyField,
)

from django.contrib.auth.models import User

from .models import  Movie, Playlist, PlaylistMovie


class MovieSerializer(ModelSerializer):
    class Meta:
        model = Movie
        fields = '__all__'


class PlaylistSerializer(ModelSerializer):
    user = ReadOnlyField(source='user.id')
    movies = MovieSerializer(many=True, read_only=True)

    class Meta:
        model = Playlist
        fields = '__all__'

    def create(self, validated_data):
        user = self.context['request'].user
        playlist = Playlist.objects.create(user=user, **validated_data)
        return playlist

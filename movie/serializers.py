from rest_framework.serializers import (
        ModelSerializer,
        SerializerMethodField,
        ReadOnlyField,
)
from .models import Movie, Playlist, Review, PlaylistMovie


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


class InPlaylistSerializer(ModelSerializer):
    poster_url = SerializerMethodField()

    def get_poster_url(self, obj):
        movie = PlaylistMovie.objects.filter(playlist=obj).first().movie
        if movie:
            return movie.poster_url
        return ""

    class Meta:
        model = Playlist
        fields = ('id', 'title', 'description', 'poster_url')


class ReviewSerializer(ModelSerializer):
    username = SerializerMethodField()

    def get_username(self, obj):
        return obj.user.username

    class Meta:
        model = Review
        fields = '__all__'

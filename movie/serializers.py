from rest_framework.serializers import (
        ModelSerializer,
        SerializerMethodField,
        ReadOnlyField,
        CharField,
)
from .models import Movie, Playlist, Review, PlaylistMovie, BlendedPlaylist


class MovieSerializer(ModelSerializer):
    class Meta:
        model = Movie
        fields = '__all__'


class PlaylistSerializer(ModelSerializer):
    user = CharField(required=False)
    username = ReadOnlyField(source='user.username')
    movies = MovieSerializer(many=True, read_only=True)
    is_blend = SerializerMethodField()

    def get_is_blend(self, obj):
        return BlendedPlaylist.objects.filter(playlist=obj).exists()

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
    username = ReadOnlyField(source='user.username')
    profile_picture = SerializerMethodField()
    title = ReadOnlyField(source='movie.title')
    release_date = ReadOnlyField(source='movie.release_date')

    def get_profile_picture(self, data):
        if data.user.profile_picture:
            return data.user.profile_picture.url
        return None

    class Meta:
        model = Review
        fields = '__all__'

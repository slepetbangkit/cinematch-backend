import datetime

from django.contrib.auth import password_validation as validators
from rest_framework.serializers import (
        ModelSerializer,
        CharField,
        EmailField,
        SerializerMethodField,
        ValidationError,
)
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import CustomUser, UserFollowing, UserActivity
from movie.models import Playlist
from movie.serializers import PlaylistSerializer


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        token['email'] = user.email

        return token


class RegisterSerializer(ModelSerializer):
    password = CharField(
        write_only=True,
        required=True,
        validators=[validators.validate_password])
    email = EmailField(
        required=True,
        validators=[UniqueValidator(queryset=CustomUser.objects.all(),
                                    message="Email already exists.")]
    )
    username = CharField(
        required=True,
        validators=[UniqueValidator(queryset=CustomUser.objects.all(),
                                    message="Username already exists.")]
    )
    token = SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password', 'token')

    def get_token(self, user):
        refresh = MyTokenObtainPairSerializer.get_token(user)

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

    def create(self, validated_data):
        user = CustomUser.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
        )

        user.set_password(validated_data['password'])
        user.save()

        Playlist.objects.create(
            title="Liked Movies",
            is_favorite=True,
            user=user
        )
        return user


class ProfileSerializer(ModelSerializer):
    is_followed = SerializerMethodField()
    is_self = SerializerMethodField()
    playlists = SerializerMethodField()

    def get_is_followed(self, obj):
        current_user = self.context['request'].user
        if current_user == obj:
            return False
        return UserFollowing.objects. \
            filter(user=current_user, following_user=obj).exists()

    def get_is_self(self, obj):
        return self.context['request'].user == obj

    def get_playlists(self, obj):
        playlists = Playlist.objects.filter(user=obj)
        return PlaylistSerializer(playlists, many=True).data

    class Meta:
        model = CustomUser
        fields = (
            'id',
            'username',
            'is_self',
            'is_followed',
            'profile_picture',
            'bio',
            'follower_count',
            'following_count',
            'playlists',
        )


class SearchProfileSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            'id',
            'username',
            'profile_picture',
        )


class UserFollowingSerializer(ModelSerializer):
    class Meta:
        model = UserFollowing
        fields = '__all__'

    def validate(self, data):
        """
        Check that the following user is different from current user.
        """
        if data['user'].id == data['following_user'].id:
            raise ValidationError("Can't follow currently logged in user.")
        return data

    def create(self, data):
        user = data['user']
        following_user = data['following_user']

        user.following_count = user.following_count + 1
        user.save()
        following_user.follower_count = following_user.follower_count + 1
        following_user.save()

        return UserFollowing.objects.create(
                user=user,
                following_user=following_user,)

    def delete(self, data):
        user = data['user']
        following_user = data['following_user']

        UserFollowing.objects.get(
                user=user.id, following_user=following_user.id).delete()

        user.following_count = user.following_count - 1
        user.save()
        following_user.follower_count = following_user.follower_count - 1
        following_user.save()


class UserFollowerListSerializer(ModelSerializer):
    id = SerializerMethodField()
    username = SerializerMethodField()

    def get_username(self, data):
        return str(CustomUser.objects.get(id=data.user.id))

    def get_id(self, data):
        return str(data.user.id)

    class Meta:
        model = CustomUser
        fields = ('id', 'username')


class UserFollowingListSerializer(ModelSerializer):
    id = SerializerMethodField()
    username = SerializerMethodField()

    def get_username(self, data):
        return str(CustomUser.objects.get(id=data.following_user.id))

    def get_id(self, data):
        return str(data.following_user.id)

    class Meta:
        model = CustomUser
        fields = ('id', 'username')


class UserActivitySerializer(ModelSerializer):
    date = SerializerMethodField()

    def get_date(self, obj):
        return obj.created_at.strftime("%d %b %Y")

    class Meta:
        model = UserActivity
        exclude = ('created_at',)

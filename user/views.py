from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import CustomUser, UserFollowing, UserActivity
from .serializers import (
        MyTokenObtainPairSerializer,
        RegisterSerializer,
        ProfileSerializer,
        SearchProfileSerializer,
        UserFollowingSerializer,
        UserFollowingListSerializer,
        UserFollowerListSerializer,
        UserActivitySerializer,
)


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class RegisterView(CreateAPIView):
    queryset = CustomUser.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            if serializer.is_valid(raise_exception=False):

                user = super().create(request, *args, **kwargs)

                return Response({
                    "error": False,
                    "message": "Successfully registered an account.",
                    "token": user.data["token"]
                }, status.HTTP_201_CREATED)

            return Response({
                "error": True,
                'message': serializer.errors,
            }, status.HTTP_400_BAD_REQUEST)

        except Exception:
            return Response({
                "error": True,
                "message": "An error has occured.",
            }, status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProfileView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, username):
        try:
            user = CustomUser.objects.get(username=username)
            serializer = ProfileSerializer(
                user,
                many=False,
                context={'request': request},
            )
            return Response(serializer.data)
        except CustomUser.DoesNotExist:
            return Response({
                "error": True,
                "message": "User not found.",
            }, status.HTTP_404_NOT_FOUND)

        except Exception:
            return Response({
                "error": True,
                "message": "An error has occured.",
            }, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request, username):
        try:
            user = request.user
            if username == str(user):
                serializer = ProfileSerializer(user,
                                               data=request.data,
                                               partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response({
                        "error": False,
                        "message": "Successfully updated profile.",
                    }, status.HTTP_200_OK)
                return Response({
                    "error": True,
                    'message': serializer.errors,
                }, status.HTTP_400_BAD_REQUEST)
            return Response({
                "error": True,
                'message': "Unauthorized.",
            }, status.HTTP_403_FORBIDDEN)
        except Exception:
            return Response({
                "error": True,
                "message": "An error has occured.",
            }, status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserFollowingView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, username):
        try:
            user = CustomUser.objects.get(username=username)
            followings_serialized = UserFollowingListSerializer(
                                        UserFollowing.objects.filter(
                                            user=user
                                        ),
                                        many=True
            )
            followers_serialized = UserFollowerListSerializer(
                                        UserFollowing.objects.filter(
                                            following_user=user
                                        ),
                                        many=True
            )
            data = {
                "following_count": user.following_count,
                "follower_count": user.follower_count,
                "followings": followings_serialized.data,
                "followers": followers_serialized.data,
            }
            return Response(data, status.HTTP_200_OK)

        except CustomUser.DoesNotExist:
            return Response({
                "error": True,
                "message": "User not found.",
            }, status.HTTP_404_NOT_FOUND)

        except Exception:
            return Response({
                "error": True,
                "message": "An error has occured.",
            }, status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception:
            return Response({
                "error": True,
                "message": "An error has occured.",
            }, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, username):
        try:
            user = request.user
            following_user = CustomUser.objects.get(username=username)
            serializer = UserFollowingSerializer(
                    data={"user": user.id,
                          "following_user": following_user.id})
            if serializer.is_valid():
                serializer.save()
                UserActivity.objects.create(
                    username=user,
                    type="FOLLOWED_USER",
                    followed_username=following_user,
                    description=f"{user.username} has started following {username}"
                )
                return Response({
                    "error": False,
                    "message": "Successfully followed user.",
                }, status.HTTP_200_OK)
            return Response({
                "error": True,
                'message': serializer.errors,
            }, status.HTTP_400_BAD_REQUEST)
        except CustomUser.DoesNotExist:
            return Response({
                "error": True,
                "message": "User not found.",
            }, status.HTTP_404_NOT_FOUND)
        except Exception:
            return Response({
                "error": True,
                "message": "An error has occured.",
            }, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, username):
        try:
            user = request.user
            following_user = CustomUser.objects.get(username=username)
            UserFollowingSerializer.delete(self, data={
                "user": user,
                "following_user": following_user
            })
            return Response({
                "error": False,
                "message": "Successfully unfollowed user.",
            }, status.HTTP_200_OK)
        except UserFollowing.DoesNotExist:
            return Response({
                "error": True,
                "message": "Following user not found.",
            }, status.HTTP_404_NOT_FOUND)
        except Exception:
            return Response({
                "error": True,
                "message": "An error has occured.",
            }, status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getActivities(request):
    followed_users = UserFollowing.objects.filter(user=request.user) \
        .values_list('following_user__username')
    activities = UserActivity.objects.filter(username__in=followed_users) \
        .order_by("-created_at")[:20]
    serialized = UserActivitySerializer(activities, many=True)
    return Response({
                "error": False,
                "activities": serialized.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def searchProfile(request):
    search_query = request.GET.get('query')
    user = CustomUser.objects.filter(username__contains=search_query)
    serializer = SearchProfileSerializer(user, many=True)
    return Response({
                "error": False,
                "users": serializer.data
    })

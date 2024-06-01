from django.http import Http404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Movie, Playlist, PlaylistMovie
from .serializers import (
        MovieSerializer,
        PlaylistSerializer,
)

class MovieView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            movies = Movie.objects.all()
            serializer = MovieSerializer(movies, many=True)
            return Response(serializer.data)
        except Exception:
            return Response({
                "error": True,
                "message": "An error has occurred.",
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            serializer = MovieSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "error": False,
                    "message": "Successfully added movie.",
                }, status.HTTP_201_CREATED)
            return Response({
                "error": True,
                'message': serializer.errors,
            }, status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({
                "error": True,
                "message": "An error has occured.",
                "Exception": Exception,
            }, status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self, request):
        try:
            movie = Movie.objects.get(pk=request.data['id'])
            movie.delete()
            return Response({
                "error": False,
                "message": "Successfully deleted movie.",
            }, status.HTTP_200_OK)
        except Movie.DoesNotExist:
            return Response({
                "error": True,
                "message": "Movie not found.",
            }, status.HTTP_404_NOT_FOUND)
        except Exception:
            return Response({
                "error": True,
                "message": "An error has occured.",
            }, status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def patch(self, request):
        try:
            movie = Movie.objects.get(pk=request.data['id'])
            serializer = MovieSerializer(movie, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "error": False,
                    "message": "Successfully updated movie.",
                }, status.HTTP_200_OK)
            return Response({
                "error": True,
                'message': serializer.errors,
            }, status.HTTP_400_BAD_REQUEST)
        except Movie.DoesNotExist:
            return Response({
                "error": True,
                "message": "Movie not found.",
            }, status.HTTP_404_NOT_FOUND)
        except Exception:
            return Response({
                "error": True,
                "message": "An error has occured.",
            }, status.HTTP_500_INTERNAL_SERVER_ERROR)

class PlaylistView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            playlists = Playlist.objects.filter(user=request.user)

            # if playlist is not found, return user not have any playlist
            if not playlists:
                return Response({
                    "error": True,
                    "message": "User does not have any playlists.",
                }, status.HTTP_404_NOT_FOUND)
            
            serializer = PlaylistSerializer(playlists, many=True)
            return Response(serializer.data)
        except Exception:
            return Response({
                "error": True,
                "message": "An error has occured.",
            }, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            serializer = PlaylistSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({
                "error": True,
                "message": "An error has occured.",
            }, status.HTTP_500_INTERNAL_SERVER_ERROR)

class PlaylistDetailView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        try:
            playlist = Playlist.objects.get(pk=pk)
            serializer = PlaylistSerializer(playlist)
            return Response(serializer.data)
        except Playlist.DoesNotExist:
            return Response({
                "error": True,
                "message": "Playlist not found.",
            }, status.HTTP_404_NOT_FOUND)
        except Exception:
            return Response({
                "error": True,
                "message": "An error has occured.",
            }, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request, pk):
            try:  
                playlist = Playlist.objects.get(pk=pk)

                # Check if user is the owner of the playlist
                if playlist.user != request.user:
                    return Response({
                        "error": True,
                        "message": "You do not have permission to edit this playlist.",
                    }, status=status.HTTP_403_FORBIDDEN)
                

                data = request.data
                
                # Update title and description
                playlist.title = data.get('title', playlist.title)
                playlist.description = data.get('description', playlist.description)
                playlist.save()
                
                # Add new movies
                new_movies = data.get('new_movie', [])
                for movie_id in new_movies:
                    try:
                        movie = Movie.objects.get(pk=movie_id)
                        PlaylistMovie.objects.get_or_create(playlist=playlist, movie=movie)
                    except Movie.DoesNotExist:
                        continue

                # Delete movies
                delete_movies = data.get('delete_movie', [])
                for movie_id in delete_movies:
                    try:
                        movie = Movie.objects.get(pk=movie_id)
                        PlaylistMovie.objects.filter(playlist=playlist, movie=movie).delete()
                    except Movie.DoesNotExist:
                        continue
                
                serializer = PlaylistSerializer(playlist)
                return Response(serializer.data)
            except Playlist.DoesNotExist:
                return Response({
                    "error": True,
                    "message": "Playlist not found.",
                }, status.HTTP_404_NOT_FOUND)
            except Exception:
                return Response({
                    "error": True,
                    "message": "An error has occured.",
                }, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, pk):
        try:
            playlist = Playlist.objects.get(pk=pk)

            # Check if user is the owner of the playlist
            if playlist.user != request.user:
                return Response({
                    "error": True,
                    "message": "You do not have permission to delete this playlist.",
                }, status=status.HTTP_403_FORBIDDEN)
            playlist.delete()
            return Response({"message": "Playlist deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except Playlist.DoesNotExist:
            return Response({
                "error": True,
                "message": "Playlist not found.",
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return Response({
                "error": True,
                "message": "An error has occurred.",
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

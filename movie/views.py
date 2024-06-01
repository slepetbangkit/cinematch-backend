from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Movie
from .serializers import (
        MovieSerializer,
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
                "message": "An error has occured.",
            }, status.HTTP_500_INTERNAL_SERVER_ERROR)

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
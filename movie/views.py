from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes

from .models import Movie, Playlist, PlaylistMovie, Review
from user.models import UserActivity
from .serializers import (
        MovieSerializer,
        PlaylistSerializer,
        ReviewSerializer,
        InPlaylistSerializer,
)
from rating.service import get_sentiment_score

from requests import get
from pycountry import countries, languages
import os

API_KEY = os.getenv('TMDB_API_KEY')
TMDB_API_URL = "https://api.themoviedb.org/3"


def createMovieFromTMDB(id):
    headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        }

    url_tmdb_movie_detail = f"{TMDB_API_URL}/movie/{id}?api_key={API_KEY}&language=en-US"
    response_movie_detail = get(url_tmdb_movie_detail, headers=headers)
    movie_detail_data = response_movie_detail.json()

    # return 502 if TMDB API is down
    if (response_movie_detail.status_code in (401, 404) or
            response_movie_detail.status_code != 200):
        return Response({
            "error": True,
            "message": f"TMDB: {response_movie_detail.json().get('status_message')}",
        }, status.HTTP_502_BAD_GATEWAY)

    url_tmdb_movie_credits = f"{TMDB_API_URL}/movie/{id}/credits?api_key={API_KEY}"
    response_movie_credits = get(url_tmdb_movie_credits, headers=headers)
    movie_credits_data = response_movie_credits.json().get('crew', [])

    for crew in movie_credits_data:
        if crew['job'] == 'Director':
            director = crew['name']
            break

    movie = Movie.objects.create(
                tmdb_id=movie_detail_data["id"],
                title=movie_detail_data["title"],
                poster_url=f"https://image.tmdb.org/t/p/original/{movie_detail_data['poster_path']}",
                description=movie_detail_data["overview"],
                director=director,
                release_date=movie_detail_data["release_date"],
                rating=0.0
            )
    return movie


class MovieView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            # if search query is provided, fetch themoviedb api
            search_query = request.GET.get('search')
            if search_query:
                url = f"{TMDB_API_URL}/search/movie?query={search_query}"
                headers = {
                    "accept": "application/json",
                    "Authorization": f"Bearer {API_KEY}"
                }

                response = get(url, headers=headers)

                # return 502 if TMDB API is down
                if (response.status_code in [401, 404]
                        or response.status_code != 200):
                    error_message = response.json().get('status_message')
                    return Response({
                        "error": True,
                        "message": f"TMDB :{error_message}",
                    }, status.HTTP_502_BAD_GATEWAY)

                results = []
                movies = response.json()["results"]
                for movie in movies:
                    id = movie["id"]
                    movie_credits_url = f"{TMDB_API_URL}/movie/{id}" \
                                        + f"/credits?api_key={API_KEY}"
                    response_movie_credits = get(
                            movie_credits_url,
                            headers=headers
                    )
                    movie_credits_data = response_movie_credits.json() \
                        .get('crew', [])

                    for crew in movie_credits_data:
                        if crew['job'] == 'Director':
                            director = crew['name']
                            break

                    results.append({
                        "tmdb_id": id,
                        "title": movie["title"],
                        "poster_url": "https://image.tmdb.org/t/p/original/"
                                      + f"{movie['poster_path']}",
                        "description": movie["overview"],
                        "director": director,
                        "release_date": movie["release_date"],
                    })

                return Response(
                    results
                )

            # else, return movies already saved in the backend database
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
            serializer = MovieSerializer(
                    movie,
                    data=request.data,
                    partial=True
            )
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


class MovieDetailTMDBView(APIView):
    permission_classes = (IsAuthenticated,)

    def get_sentiment(self, rating, review_count):
        percentage = rating * 100

        if 95 <= percentage <= 100:
            return "Overwhelmingly Positive"
        elif 80 <= percentage < 95:
            if review_count >= 10:
                return "Very Positive"
            if review_count > 0:
                return "Positive"
        elif 70 <= percentage < 80:
            return "Mostly Positive"
        elif 40 <= percentage < 70:
            return "Mixed"
        elif 20 <= percentage < 40:
            if review_count >= 100:
                return "Mostly Negative"
            else:
                return "Negative"
        elif 0 <= percentage < 20:
            if review_count >= 10:
                return "Overwhelmingly Negative"
            if review_count > 0:
                return "Very Negative"
        return "N/A"

    def get(self, request, pk):
        try:
            headers = {
                    "accept": "application/json",
                    "Authorization": f"Bearer {API_KEY}"
            }

            url = f"{TMDB_API_URL}/movie/{pk}?api_key={API_KEY}&append_to_response=videos,credits,similar"
            response = get(url, headers=headers)

            # return 502 if TMDB API is down
            if response.status_code == 404 or response.status_code == 401 or response.status_code != 200:
                return Response({
                    "error": True,
                    "message": f"TMDB :{response.json().get('status_message')} ",
                }, status.HTTP_502_BAD_GATEWAY)

            movie_details = response.json()

            # Get director
            movie_credits_data = movie_details.get('credits', {}).get('crew', [])
            for crew in movie_credits_data:
                if crew['job'] == 'Director':
                    director = crew['name']
                    break

            # Get trailer link
            trailer_link = None
            for video in movie_details.get('videos', {}).get('results', []):
                if (video['site'] == 'YouTube' and video['type'] == 'Trailer'):
                    trailer_link = f"https://www.youtube.com/watch?v={video['key']}"
                    break

            # Get cast ( name, char, poster )
            cast = []
            for actor in movie_details.get('credits', {}).get('cast', [])[:5]:
                cast.append({
                    "name": actor['name'],
                    "character": actor['character'],
                    "profile_url": f"https://image.tmdb.org/t/p/original/{actor['profile_path']}",
                })

            # Get crew ( name, char, poster )
            crew = []
            for crew_member in movie_details.get('credits', {}).get('crew', [])[:5]:
                crew.append({
                    "name": crew_member['name'],
                    "job": crew_member['job'],
                    "profile_url": f"https://image.tmdb.org/t/p/original/{crew_member['profile_path']}",
                })

            # Get similar movies
            similar_movies = []
            for similar_movie in movie_details.get('similar', {}).get('results', [])[:5]:
                similar_movies.append({
                    "tmdb_id": similar_movie['id'],
                    "title": similar_movie['title'],
                    "poster_url": f"https://image.tmdb.org/t/p/original/{similar_movie['poster_path']}",
                })

            try:
                movie = Movie.objects.get(tmdb_id=pk)
                rating = movie.rating
                review_count = movie.review_count
                playlists = [pm.playlist for pm in PlaylistMovie.objects.filter(
                    movie=movie,
                    playlist__user=request.user,
                )]
                in_playlists = InPlaylistSerializer(playlists, many=True).data
                is_liked = True
            except Movie.DoesNotExist:
                rating = 0.0
                review_count = 0
                is_liked = False
                in_playlists = []

            genres = [genre["name"] for genre in movie_details["genres"]]

            origin_countries = [
                countries.get(alpha_2=country).name
                for country in movie_details["origin_country"]
            ]

            language = languages.get(alpha_2=movie_details["original_language"]).name

            data = {
                "tmdb_id": movie_details["id"],
                "title": movie_details["title"],
                "overall_sentiment": self.get_sentiment(rating, review_count),
                "is_liked": is_liked,
                "in_playlists": in_playlists,
                "origin_countries": origin_countries,
                "languages": language,
                "genres": genres,
                "poster_url": f"https://image.tmdb.org/t/p/original/{movie_details['poster_path']}",
                "backdrop_url": f"https://image.tmdb.org/t/p/original/{movie_details['backdrop_path']}",
                "description": movie_details["overview"],
                "director": director,
                "release_date": movie_details["release_date"],
                "runtime": movie_details["runtime"],
                "rating": rating,
                "trailer_link": trailer_link,
                "cast": cast,
                "crew": crew,
                "similar_movies": similar_movies,
            }

            return Response(data, status.HTTP_200_OK)
        except Exception:
            return Response({
                "error": True,
                "message": "An error has occured.",
                "Exception": Exception,
            }, status.HTTP_500_INTERNAL_SERVER_ERROR)


class PlaylistView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            playlists = Playlist.objects.filter(user=request.user)
            serializer = PlaylistSerializer(playlists, many=True)
            return Response(serializer.data)
        except Exception:
            return Response({
                "error": True,
                "message": "An error has occured.",
            }, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            serializer = PlaylistSerializer(
                    data=request.data,
                    context={'request': request}
            )
            if serializer.is_valid():
                serializer.save()
                return Response(
                        serializer.data,
                        status=status.HTTP_201_CREATED
                )
            return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
            )
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
                message = "You do not have permission to edit this playlist."
                return Response({
                    "error": True,
                    "message": message,
                }, status=status.HTTP_403_FORBIDDEN)

            data = request.data

            # Update title and description
            playlist.title = data.get('title', playlist.title)
            playlist.description = data.get('description',
                                            playlist.description)
            playlist.save()

            # Add new movies
            new_movies = data.get('new_movie_tmdb_id', [])
            for movie_id in new_movies:
                movie_title = ""
                movie = Movie.objects.filter(tmdb_id=movie_id)

                if movie.exists():
                    movie = movie.first()
                else:
                    movie = createMovieFromTMDB(movie_id)

                PlaylistMovie.objects.get_or_create(playlist=playlist,
                                                    movie=movie)
                movie_title = movie.title
                description = f"{request.user} added {movie_title} "
                activity_type = ""

                if playlist.is_favorite:
                    description += "to their liked movies"
                    activity_type = "LIKED_MOVIE"
                else:
                    description += "to their playlist"
                    activity_type = "ADDED_MOVIE_TO_PLAYLIST"

                UserActivity.objects.create(
                    username=request.user,
                    movie_tmdb_id=movie_id,
                    description=description,
                    type=activity_type
                )

            # Delete movies
            delete_movies = data.get('delete_movie_tmdb_id', [])
            for movie_id in delete_movies:
                try:
                    movie = Movie.objects.get(tmdb_id=movie_id)
                    PlaylistMovie.objects.filter(
                            playlist=playlist, movie=movie
                            ).delete()
                except Movie.DoesNotExist:
                    continue

            serializer = PlaylistSerializer(playlist)
            return Response(serializer.data)
        except Playlist.DoesNotExist:
            return Response({
                "error": True,
                "message": "Playlist not found.",
            }, status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "error": True,
                "message": "An error has occured.",
                "Exception": e,

            }, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, pk):
        try:
            playlist = Playlist.objects.get(pk=pk)

            # Check if user is the owner of the playlist
            message = "You do not have permission to delete this playlist."
            if playlist.user != request.user:
                return Response({
                    "error": True,
                    "message": message,
                }, status=status.HTTP_403_FORBIDDEN)
            playlist.delete()
            return Response(
                    {"message": "Playlist deleted successfully."},
                    status=status.HTTP_204_NO_CONTENT)
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


class ReviewView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        try:
            movie = Movie.objects.get(tmdb_id=pk)
            reviews = Review.objects.filter(movie=movie)
            return Response({
                "error": False,
                "movie": {
                    "title": movie.title,
                    "release_date": movie.release_date,
                },
                "reviews": ReviewSerializer(reviews, many=True).data
            }, status.HTTP_200_OK)
        except Movie.DoesNotExist:
            return Response({
                "error": False,
                "reviews": [],
            }, status.HTTP_200_OK)

    def post(self, request, pk):
        try:
            movie = Movie.objects.filter(tmdb_id=pk)
            if movie.exists():
                movie = movie.first()
            else:
                movie = createMovieFromTMDB(pk)
            description = request.data['description']
            sentiment_score = get_sentiment_score(description)

            serializer = ReviewSerializer(data={
                'user': request.user.id,
                'movie': movie.id,
                'description': description,
                'rating': sentiment_score,
            }, context={'request': request})

            if serializer.is_valid():
                serializer.save()
                movie.rating = ((movie.rating * movie.review_count)
                                + sentiment_score) / (movie.review_count + 1)
                movie.review_count += 1
                movie.save()
                description = f"{request.user.username} left a review on {movie.title}"
                activity_type = "REVIEWED_MOVIE"
                UserActivity.objects.create(
                    username=request.user,
                    movie_tmdb_id=movie.tmdb_id,
                    description=description,
                    type=activity_type
                )
                return Response({
                    "error": False,
                    "data": serializer.data
                }, status=status.HTTP_201_CREATED)
            return Response({
                "error": True,
                "message": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            raise e
            return Response({
                "error": True,
                "message": "An error has occured.",
            }, status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getReviewDetailById(request, pk):
    try:
        review = Review.objects.get(id=pk)
        serializer = ReviewSerializer(review)
        return Response({
                    "error": False,
                    "data": serializer.data
        })
    except Review.DoesNotExist:
        return Response({
            "error": True,
            "message": "Review not found.",
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception:
        return Response({
            "error": True,
            "message": "An error has occurred.",
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

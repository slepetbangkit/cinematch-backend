from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes

from .models import Movie, Playlist, PlaylistMovie, Review, BlendedPlaylist
from user.models import UserActivity, UserFollowing, CustomUser
from user.serializers import UserActivitySerializer
from .serializers import (
        MovieSerializer,
        PlaylistSerializer,
        ReviewSerializer,
        InPlaylistSerializer,
)
from rating.service import get_sentiment_score
from recommendations.service import recommend_movies

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
        if review_count >= 10:
            if 95 <= percentage <= 100:
                return "Overwhelmingly Positive"
            if 85 <= percentage <= 100:
                return "Very Positive"
            if 20 <= percentage < 40:
                return "Mostly Negative"
            if 0 < review_count < 10:
                return "Overwhelmingly Negative"
        if review_count > 0:
            if 80 <= percentage <= 100 and review_count > 0:
                return "Positive"
            if 70 <= percentage < 80 and review_count > 0:
                return "Mostly Positive"
            if 40 <= percentage < 70 and review_count > 0:
                return "Mixed"
            if 20 <= percentage < 40:
                return "Negative"
            if 0 < review_count < 10:
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
                is_liked = PlaylistMovie.objects.filter(
                        movie=movie,
                        playlist__user=request.user,
                        playlist__is_favorite=True,
                ).exists()
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
            blended_playlists = BlendedPlaylist.objects.filter(
                    second_user=request.user
            ).values('playlist__pk')
            print(blended_playlists)
            playlists = Playlist.objects.filter(user=request.user) | \
                Playlist.objects.filter(pk__in=blended_playlists)
            serializer = PlaylistSerializer(playlists, many=True)
            return Response(serializer.data)
        except Exception as e:
            raise e
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
            blended_playlist = BlendedPlaylist.objects.filter(
                    playlist=playlist, second_user=request.user
            )
            # Check if user is the owner of the playlist
            if (playlist.user != request.user
                    and not blended_playlist.exists()):
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
                    description += "to their movie list"
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
        except Exception:
            return Response({
                "error": True,
                "message": "An error has occured.",
            }, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, pk):
        try:
            playlist = Playlist.objects.get(pk=pk)
            blended_playlist = BlendedPlaylist.objects.filter(
                    playlist=playlist, second_user=request.user
            )
            # Check if user is the owner of the playlist
            if (playlist.user != request.user
                    and not blended_playlist.exists()):
                message = "You do not have permission to edit this playlist."
                return Response({
                    "error": True,
                    "message": message,
                }, status=status.HTTP_403_FORBIDDEN)

            playlist.delete()
            return Response(
                    {"message": "Playlist deleted successfully."},
                    status=status.HTTP_200_OK)
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
            is_reviewed = reviews.filter(user=request.user).exists()
            return Response({
                "error": False,
                "movie": {
                    "title": movie.title,
                    "release_date": movie.release_date,
                },
                "is_reviewed": is_reviewed,
                "reviews": ReviewSerializer(reviews, many=True).data
            }, status.HTTP_200_OK)
        except Movie.DoesNotExist:
            return Response({
                "error": False,
                "is_reviewed": False,
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
                    review_id=serializer.data['id'],
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
        except Exception:
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


class HomeView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        try:
            results = {
                "recommended": [],
                "friends": [],
                "verdict": [],
                "top_rated": []
            }
            recommendations_available = False
            if (request.user.is_authenticated
                and PlaylistMovie.objects.
                    filter(playlist__user=request.user).exists()):
                # get all movies from playlist
                playlist_movies = PlaylistMovie.objects.filter(
                        playlist__user=request.user
                )
                selected_movie_indices = [pm.movie.tmdb_id for pm in playlist_movies]
                recommended_movies = recommend_movies(
                        selected_movie_indices,
                        10,
                )
                recommendations_available = bool(recommended_movies)
                if recommendations_available:
                    for movie in recommended_movies:
                        id_tmdb = movie
                        url = f"{TMDB_API_URL}/movie/{id_tmdb}?api_key={API_KEY}"
                        headers = {
                            "accept": "application/json",
                            "Authorization": f"Bearer {API_KEY}"
                        }
                        response = get(url, headers=headers)
                        movie_detail_data = response.json()
                        results["recommended"].append({
                            "tmdb_id": movie_detail_data["id"],
                            "title": movie_detail_data["title"],
                            "poster_url": "https://image.tmdb.org/t/p/original/"
                            + f"{movie_detail_data['poster_path']}",
                        })
            if not recommendations_available:
                # popular movie from tmdbtmdb_api_url = "https://api.themoviedb.org/3"
                url = f"{TMDB_API_URL}/movie/popular?api_key={API_KEY}"
                headers = {
                        "accept": "application/json",
                        "Authorization": f"Bearer {API_KEY}"
                    }
                response = get(url, headers=headers)

                movies = response.json()["results"]
                for movie in movies[:10]:
                    results["recommended"].append({
                        "tmdb_id": movie["id"],
                        "title": movie["title"],
                        "poster_url": "https://image.tmdb.org/t/p/original/"
                        + f"{movie['poster_path']}",
                    })

            # get friend's liked movies from playlist (is_favorite == True)
            if (request.user.is_authenticated
                    and UserFollowing.objects.filter(user=request.user).
                    exists()):
                following_users = UserFollowing.objects.filter(
                        user=request.user
                ).values_list("following_user", flat=True)

                liked_movies = PlaylistMovie.objects.filter(
                        playlist__is_favorite=True,
                        playlist__user__in=following_users,
                ).order_by('-added_at')[:10]

                for pm in liked_movies:
                    results["friends"].append({
                        "tmdb_id": pm.movie.tmdb_id,
                        "title": pm.movie.title,
                        "poster_url": pm.movie.poster_url,
                        "username": pm.playlist.user.username,
                        "profile_picture": UserActivitySerializer(
                            UserActivity.objects.filter(
                                username=pm.playlist.user
                            ).first()
                        ).data.get("profile_picture")
                    })

                verdict = Review.objects.filter(
                        user__in=following_users
                ).order_by("-created_at")[:10]
                for review in verdict:
                    results["verdict"].append({
                        "review_id": review.id,
                        "tmdb_id": review.movie.tmdb_id,
                        "release_date": review.movie.release_date,
                        "title": review.movie.title,
                        "poster_url": review.movie.poster_url,
                        "username": review.user.username,
                        "profile_picture": UserActivitySerializer(
                            UserActivity.objects.filter(
                                username=review.user
                            ).first()).data.get("profile_picture"),
                        "description": review.description,
                        "reviewed_at": review.created_at
                    })
            else:
                # get empty list for friends and all in verdict
                results["friends"] = []

                # get random 10 movies from all in movie_review
                verdict = Review.objects.all().order_by("-created_at")[:10]

                for review in verdict:
                    results["verdict"].append({
                        "review_id": review.id,
                        "tmdb_id": review.movie.tmdb_id,
                        "release_date": review.movie.release_date,
                        "title": review.movie.title,
                        "poster_url": review.movie.poster_url,
                        "username": review.user.username,
                        "profile_picture": UserActivitySerializer(
                            UserActivity.objects.filter(
                                username=review.user
                            ).first()
                        ).data.get("profile_picture"),
                        "description": review.description,
                        "reviewed_at": review.created_at,
                    })
            # get popular movies geolocation based on user's location from tmdb
            url = f"{TMDB_API_URL}/movie/top_rated?api_key={API_KEY}"
            response = get(url, headers=headers)
            movies = response.json()["results"]
            for movie in movies:
                results["top_rated"].append({
                    "tmdb_id": movie["id"],
                    "title": movie["title"],
                    "poster_url": "https://image.tmdb.org/t/p/original/"
                    + f"{movie['poster_path']}",
                })
            return Response({
                "error": False,
                "data": results
            })
        except Exception:
            return Response({
                "error": True,
                "message": "An error has occured.",
            }, status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated,])
def blendPlaylist(request, username):
    try:
        second_user = CustomUser.objects.get(username=username)
        if (not BlendedPlaylist.objects.filter(
                playlist__user=request.user, second_user=second_user
                ).exists()):
            second_liked_movies = Playlist.objects.get(
                    user=second_user,
                    is_favorite=True
            ).movies.all()[:10]
            first_liked_movies = Playlist.objects.get(
                    user=request.user,
                    is_favorite=True
            ).movies.all()[:10]
            if (first_liked_movies.count() > 0
                    and second_liked_movies.count() > 0):
                # movies =
                print(first_liked_movies)
                print(second_liked_movies)
                movies = ([m.tmdb_id for m in first_liked_movies]
                          + [m.tmdb_id for m in second_liked_movies])
                recommended_movies = recommend_movies(
                    movies,
                    20,
                )
                print(recommended_movies)
                playlist = Playlist.objects.create(
                    user=request.user,
                    title=f"{request.user.username} and {username}'s blend"
                )
                BlendedPlaylist.objects.create(
                        playlist=playlist,
                        second_user=second_user
                )
                for movie_id in recommended_movies:
                    movie = Movie.objects.filter(tmdb_id=movie_id)
                    if movie.exists():
                        movie = movie.first()
                    else:
                        movie = createMovieFromTMDB(movie_id)
                    PlaylistMovie.objects.get_or_create(playlist=playlist,
                                                        movie=movie)
                return Response({
                    "error": False,
                    "message": "ok"
                })
            return Response({
                "error": True,
                "message": "One of the users have empty Liked Movies list."
            })
        return Response({
            "error": True,
            "message": "Already blended a playlist with user."
        })
    except Playlist.DoesNotExist:
        return Response({
            "error": True,
            "message": "One of the users does not have a Liked Movies list.",
        }, status.HTTP_404_NOT_FOUND)
    except CustomUser.DoesNotExist:
        return Response({
            "error": True,
            "message": f"user {username} not found.",
        }, status.HTTP_404_NOT_FOUND)
    except Exception:
        return Response({
            "error": True,
            "message": "An error has occured.",
        }, status.HTTP_500_INTERNAL_SERVER_ERROR)

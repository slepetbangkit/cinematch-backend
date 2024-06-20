import numpy as np
from django.apps import apps
from sklearn.metrics.pairwise import cosine_similarity


CONFIG = apps.get_app_config('recommendations')
SIMILARITY = CONFIG.similarity
FEATURES = CONFIG.features
MOVIES = CONFIG.movies


def mul_recommander(selected_movie_indices):
    selected_features = FEATURES[selected_movie_indices]
    aggregated_features = np.mean(selected_features, axis=0)
    similarity = cosine_similarity(np.asarray(aggregated_features).
                                   reshape(1, -1), FEATURES).flatten()
    sorted_indices = np.argsort(similarity)[::-1]
    recommended_movies = MOVIES.iloc[sorted_indices]

    return recommended_movies


def recommend_movies(movies_id, number):
    """
    Fungsi ini menerima daftar ID film dan jumlah film yang ingin ditampilkan.
    Akan mengembalikan dan mencetak film yang direkomendasikan.
    """
    # Memeriksa ID film yang ada dalam data
    valid_movie_ids = [
            movie for movie in movies_id if movie in MOVIES['Movie_id'].values
    ]

    if not valid_movie_ids:
        print('Tidak ada film yang sesuai dengan ID yang diberikan.')
        return []

    # Mengambil indeks film yang dipilih dari DataFrame movies
    selected_movie_indices = [MOVIES[MOVIES['Movie_id'] == movie].
                              index[0] for movie in valid_movie_ids]

    # Menjalankan recommender untuk mendapatkan rekomendasi
    result = mul_recommander(selected_movie_indices)

    # Mengambil judul dari film yang dipilih
    selected_titles = MOVIES[MOVIES['Movie_id'].isin(movies_id)]['title']. \
        tolist()

    # Menampilkan judul film yang dipilih, setiap judul di baris baru
    print('Selected movies are:')
    print("\n".join(selected_titles))
    print()

    # Mengambil sejumlah judul film yang direkomendasikan,
    # mulai setelah film yang dipilih
    # (kalo mau ngambil Movie_id bisa dirubah parameternya)
    recommended_titles = result['title']. \
        iloc[len(movies_id):len(movies_id) + number].tolist()

    # Menampilkan sejumlah film yang direkomendasikan,
    # setiap judul di baris baru
    print(f'{number} recommended movies:')
    print("\n".join(recommended_titles))

    recommended_movies_id = result['Movie_id']. \
        iloc[len(movies_id):len(movies_id) + number].tolist()

    return recommended_movies_id

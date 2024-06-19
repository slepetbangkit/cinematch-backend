import os
import zipfile
import urllib.request
from django.conf import settings
from django.apps import AppConfig


class RecommendationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "recommendations"

    def ready(self):
        import pickle

        print('\n[RECOMMENDATIONS MODEL]')
        path = 'recommendations/similarity_model'
        file_path = f'{path}/similarity.pkl'
        if os.path.isfile(file_path):
            print(f"{file_path} FOUND!")
        else:
            print(f"{file_path} NOT FOUND!")

            bucket_name = settings.GS_BUCKET_NAME
            object_path = f'{bucket_name}/models/similarity/similarity_model/similarity.pkl'
            url = f"https://storage.googleapis.com/{object_path}"

            print("Downloading from bucket...\n", url, "\n")
            urllib.request.urlretrieve(url, file_path)
            print(
                "Downloaded object {} from bucket {} to local file {}."
                .format(
                    'similarity_model.zip', bucket_name, file_path
                )
            )
        loaded_data = {}
        for filename in os.listdir(f"{path}/"):
            filepath = os.path.join(path, filename)
            with open(filepath, 'rb') as file:
                loaded_data[filename[:-4]] = pickle.load(file)
            print(f"--{filepath} loaded")
        print()
        self.movies = loaded_data["movies"]
        self.features = loaded_data["features"]
        self.similarity = loaded_data["similarity"]

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
        from google.cloud import storage

        print('\n[RECOMMENDATIONS MODEL]')
        path = 'recommendations/similarity_model'

        if os.path.isdir(f"{path}/"):
            print("Directory FOUND!")
        else:
            print("Directory NOT FOUND!")

            if not os.path.isfile(f"{path}.zip"):
                bucket_name = settings.GS_BUCKET_NAME
                object_path = f'{bucket_name}/models/similarity/similarity_model.zip'
                url = f"https://storage.googleapis.com/{object_path}"

                print("Downloading from bucket...\n", url, "\n")
                urllib.request.urlretrieve(url, f"{path}.zip")
                print(
                    "Downloaded object {} from bucket {} to local file {}."
                    .format(
                        'similarity_model.zip', bucket_name, f'{path}.zip'
                    )
                )
            print("\nExtracting similarity_model.zip file...")
            with zipfile.ZipFile(f'{path}.zip', 'r') as zip_ref:
                zip_ref.extractall(f'{path}/')
            os.remove(f'{path}.zip')

        loaded_data = {}
        for filename in os.listdir(f"{path}/"):
            filepath = os.path.join(path, filename)
            with open(filepath, 'rb') as file:
                loaded_data[filename[:-4]] = pickle.load(file)
            print(f"--{filename} loaded")
        print()

        self.movies = loaded_data["movies"]
        self.features = loaded_data["features"]
        self.similarity = loaded_data["similarity"]

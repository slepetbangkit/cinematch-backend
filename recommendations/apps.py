import os
import zipfile
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
                print("Downloading from bucket..\n")

                storage_client = storage.Client()
                bucket_name = settings.GS_BUCKET_NAME
                bucket = storage_client.bucket(bucket_name)
                blob = bucket.blob('models/similarity/similarity_model.zip')
                blob.download_to_filename(f'{path}.zip')
                print(
                    "\n\nDownloaded object {} from bucket {} to local file {}."
                    .format(
                        'similarity_model.zip', bucket_name, f'{path}.zip'
                    )
                )
            print("\n\nExtracting similarity_model.zip\n")
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


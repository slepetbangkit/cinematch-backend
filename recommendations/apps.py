import os
from django.apps import AppConfig


class RecommendationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "recommendations"

    def ready(self):
        import pickle

        print('\n[RECOMMENDATIONS MODEL]')
        path = 'recommendations/similarity_model'

        if os.path.isdir(f"{path}/"):
            print("Directory FOUND!")
        else:
            print("Directory NOT FOUND!")
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

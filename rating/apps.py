from django.apps import AppConfig


class RatingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = "rating"

    def ready(self):
        import tensorflow as tf
        import tensorflow_text as text

        load_options = tf.saved_model.LoadOptions(
            experimental_io_device='/job:localhost'
        )
        path = 'rating/rating_model/'
        self.sentiment_model = tf.saved_model.load(path, options=load_options)

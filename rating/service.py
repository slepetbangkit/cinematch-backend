from django.conf import settings
import tensorflow as tf
import tensorflow_text as text


def load_model(path):
    load_options = tf.saved_model.LoadOptions(
            experimental_io_device='/job:localhost'
    )
    return tf.saved_model.load(path, options=load_options)


def predict_sentiment(model, description):
    results = model(description)
    return tf.sigmoid(results).numpy().item()


def get_sentiment_score(description):
    model = load_model(f'{settings.BASE_DIR}/rating/rating_model')
    desc = tf.convert_to_tensor([description.lower()], dtype=tf.string)
    return predict_sentiment(model, desc)

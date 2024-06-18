import tensorflow as tf
from django.apps import apps

CONFIG = apps.get_app_config('rating')
MODEL = CONFIG.sentiment_model


def predict_sentiment(description):
    results = MODEL(description)
    return tf.sigmoid(results).numpy().item()


def get_sentiment_score(description):
    desc = tf.convert_to_tensor([description.lower()], dtype=tf.string)
    return predict_sentiment(desc)

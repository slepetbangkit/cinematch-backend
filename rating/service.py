from .utils import load_model, predict_sentiment
from django.conf import settings

import tensorflow as tf

model = load_model(f'{settings.BASE_DIR}/rating/rating_model')


def get_sentiment_score(description):
    desc = tf.convert_to_tensor([description.lower()], dtype=tf.string)
    return predict_sentiment(model, desc)

import tensorflow as tf
import tensorflow_text as text


def load_model(path):
    load_options = tf.saved_model.LoadOptions(
            experimental_io_device='/job:localhost'
    )
    return tf.saved_model.load(path, options=load_options)


def predict_sentiment(model, description):
    results = model(description)
    return round(1.0 + 4.0 * tf.sigmoid(results).numpy().item(), 2)


def preprocess_description(description):
    return description.lower()

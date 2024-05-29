import tensorflow as tf

def load_model(path):
    return tf.saved_model.load(path)

def predict_sentiment(model, description):
    processed_description = preprocess_description(description)
    results = model(processed_description)
    return results.numpy()

def preprocess_description(description):
    return description.lower()
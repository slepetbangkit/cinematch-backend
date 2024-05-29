from .utils import load_model, predict_sentiment

model = load_model('/Users/rifqiadli/Desktop/UI/Bangkit/cinematch-backend/rating/rating_model') # Change this path

def get_sentiment_score(description):
    return predict_sentiment(model, description)

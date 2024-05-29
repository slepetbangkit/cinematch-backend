from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Review
from .serializers import ReviewSerializer
from .utils import load_model, predict_sentiment

model = load_model('/Users/rifqiadli/Desktop/UI/Bangkit/cinematch-backend/rating/rating_model')

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    @action(detail=False, methods=['post'])
    def post(self, request):
        # Mengambil deskripsi dari request data
        description = request.data.get('description')
        
        # Mengecek jika deskripsi tidak diberikan
        if not description:
            return Response({'error': 'Description is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Melakukan prediksi menggunakan model yang dimuat
        score = predict_sentiment(model, description)
        
        # Membuat response dengan skor prediksi
        return Response({'input': description, 'score': score}, status=status.HTTP_200_OK)

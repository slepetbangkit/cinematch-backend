from django.urls import path
from .views import (
    ReviewViewSet
)

app_name = "rating"

urlpatterns = [
    path("predict/", ReviewViewSet.as_view(), name="rating-predict")
]

from django.contrib import admin
from .models import Movie, Review

# Register your models here.
admin.site.register((Movie, Review))

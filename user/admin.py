from django.contrib import admin
from .models import CustomUser, UserFollowing

# Register your models here.
admin.site.register((
    CustomUser,
    UserFollowing,
))

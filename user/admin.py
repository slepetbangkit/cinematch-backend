from django.contrib import admin
from .models import CustomUser, UserFollowing, UserActivity

# Register your models here.
admin.site.register((
    CustomUser,
    UserFollowing,
    UserActivity,
))

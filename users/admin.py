from django.contrib import admin
from .models import UserProfile, UserExt
# Register your models here.

admin.site.register(UserProfile)
admin.site.register(UserExt)
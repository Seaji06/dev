from django.contrib import admin
from .models import UserProfile, StudentList, UserActivity

admin.site.register(UserProfile)
admin.site.register(StudentList)
admin.site.register(UserActivity)
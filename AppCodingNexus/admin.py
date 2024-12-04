from django.contrib import admin
from .models import UserProfile, StudentList, UserActivity, Courses, Classroom, FourPicsOneWordPuzzle, PuzzleAttempt

admin.site.register(UserProfile)
admin.site.register(StudentList)
admin.site.register(UserActivity)
admin.site.register(Courses)
admin.site.register(Classroom)
admin.site.register(FourPicsOneWordPuzzle)
admin.site.register(PuzzleAttempt)
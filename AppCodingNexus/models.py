from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    studentID = models.IntegerField(null=True, blank=True)
    display_photo = models.ImageField(upload_to='profile_pics/', default='default.jpg')
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    birthday = models.DateField()
    gender = models.CharField(max_length=15, null=True, blank=True)
    role = models.CharField(max_length=20,choices=[('Student', 'Student'), ('Instructor', 'Instructor')], blank=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.user.username
        

class StudentList(models.Model):
    studentID = models.IntegerField()
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    birthday = models.DateField()
    
    def __str__(self):
        return self.firstname + " " + self.lastname

class UserActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to the User model
    activity_type = models.CharField(max_length=100)  # Type of activity (e.g., "login", "registration")
    date = models.DateTimeField(auto_now_add=True)  # Timestamp of when the activity occurred
    description = models.TextField(blank=True, null=True)  # Optional description of the activity

    def __str__(self):
        return f"{self.user.username} - {self.activity_type} on {self.date.strftime('%Y-%m-%d %H:%M:%S')}"
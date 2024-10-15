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

    def __str__(self):
        return self.user.username

class StudentList(models.Model):
    studentID = models.IntegerField()
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    birthday = models.DateField()
    
    def __str__(self):
        return self.firstname + " " + self.lastname

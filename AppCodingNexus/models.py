from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import pytz
from datetime import timedelta

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
    is_deleted = models.BooleanField(default=False)
    deletion_requested = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.user.username
        
    def mark_for_deletion(self):
        self.is_deleted = True
        self.deletion_requested = timezone.now()
        self.save()

    def cancel_deletion(self):
        self.is_deleted = False
        self.deletion_requested = None
        self.save()

    def should_be_deleted(self):
        if self.is_deleted and self.deletion_requested:
            return timezone.now() > self.deletion_requested + timezone.timedelta(days=30)
        return False

class StudentList(models.Model):
    studentID = models.IntegerField()
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    birthday = models.DateField()
    
    def __str__(self):
        return self.firstname + " " + self.lastname

class UserActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=100)
    date = models.DateTimeField()
    description = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        # Set the current time in Manila timezone if no date is provided
        if not self.date:
            manila_tz = pytz.timezone('Asia/Manila')
            self.date = timezone.now().astimezone(manila_tz)
        
        # This line automatically deletes logs older than 30 days
        seven_days_ago = timezone.now() - timedelta(days=30)
        UserActivity.objects.filter(date__lt=seven_days_ago).delete()
        
        # Save the current log
        super().save(*args, **kwargs)

    def __str__(self):
        manila_tz = pytz.timezone('Asia/Manila')
        manila_time = self.date.astimezone(manila_tz)
        return f"{self.user.username}- {self.activity_type} on {manila_time.strftime('%Y-%m-%d %H:%M:%S')}"

    @classmethod
    def cleanup_old_logs(cls):
        seven_days_ago = timezone.now() - timedelta(days=7)
        cls.objects.filter(date__lt=seven_days_ago).delete()

class Courses(models.Model):
    course_name = models.CharField(max_length=100)
    course_image = models.ImageField(upload_to='course_images/', default='default.jpg')
    pdf_file = models.FileField(upload_to='pdf_files/', default='default.pdf')

    def __str__(self):
        return self.course_name

class Classroom(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=10, unique=True)
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='instructed_classes')
    students = models.ManyToManyField(User, related_name='enrolled_classes', blank=True)
    course = models.ForeignKey('Courses', on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    invite_token = models.CharField(max_length=32, unique=True, null=True, blank=True)

    def __str__(self):
        return self.name

    def generate_invite_token(self):
        """Generate a unique invite token"""
        import uuid
        self.invite_token = uuid.uuid4().hex
        self.save()
        return self.invite_token

class FourPicsOneWordPuzzle(models.Model):
    image1 = models.ImageField(upload_to='4pics/')
    image2 = models.ImageField(upload_to='4pics/')
    image3 = models.ImageField(upload_to='4pics/')
    image4 = models.ImageField(upload_to='4pics/')
    answer = models.CharField(max_length=50)

    def __str__(self):
        return f"Puzzle {self.id}: {self.answer}"

class PuzzleAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    puzzle = models.ForeignKey(FourPicsOneWordPuzzle, on_delete=models.CASCADE)
    answer = models.CharField(max_length=50)
    is_correct = models.BooleanField()
    attempt_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.puzzle.answer} - {'Correct' if self.is_correct else 'Incorrect'}"
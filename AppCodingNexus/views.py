from django.contrib.auth.decorators import login_required
from django.http import BadHeaderError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib import messages
from django.conf import settings
from .models import StudentList, UserActivity, UserProfile
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from datetime import datetime, timedelta, timezone
from django.db.models import Q, Count
from django.utils import timezone
import random
import pytz
from django.utils.timezone import activate

#@login_required(login_url='login')
def home(request):
    return render(request, 'home.html')

def course(request):
    return render(request, 'courses.html')

def classroom(request):
    return render(request, 'classroom.html')

def about(request):
    return render(request, 'about.html')

@login_required(login_url='login')
def profile(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    return render(request, 'profile.html', {'user_profile': user_profile})

@login_required(login_url='login')
def view_profile(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    return render(request, 'viewprofile.html', {'user_profile': user_profile})

@login_required(login_url='login')
def edit_profile(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    if request.method == 'POST':
        try:
            # Update user profile information
            user_profile.firstname = request.POST.get('firstname')
            user_profile.lastname = request.POST.get('lastname')
            user_profile.bio = request.POST.get('bio', '')
            
            # Handle profile picture upload
            if 'display_photo' in request.FILES:
                user_profile.display_photo = request.FILES['display_photo']
            
            user_profile.save()
            
            # Update User model information
            request.user.username = request.POST.get('username')
            request.user.save()
            
            messages.success(request, 'Profile updated successfully!')
            return redirect('view_profile')
            
        except Exception as e:
            messages.error(request, f'Error updating profile: {str(e)}')
    
    return render(request, 'editprofile.html', {'user_profile': user_profile})

@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        old_password = request.POST.get('old-password')
        new_password = request.POST.get('new-password')
        confirm_password = request.POST.get('confirm-password')
        
        # Verify old password
        if not request.user.check_password(old_password):
            messages.error(request, 'Current password is incorrect.')
            return redirect('change_password')
        
        # Check if new passwords match
        if new_password != confirm_password:
            messages.error(request, 'New passwords do not match.')
            return redirect('change_password')
        
        # Update password
        request.user.set_password(new_password)
        request.user.save()
        
        messages.success(request, 'Password changed successfully. Please login again.')
        return redirect('login')
    
    return render(request, 'change_password.html')

@login_required(login_url='login')
def delete_account(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    if request.method == 'POST':
        try:
            user_profile.mark_for_deletion()
            logout(request)
            messages.success(request, 'Your account has been scheduled for deletion. If you log in within 30 days, the deletion will be cancelled.')
            return redirect('login')
        except Exception as e:
            messages.error(request, f'Error scheduling account deletion: {str(e)}')
    
    # Calculate days remaining if already scheduled for deletion
    days_remaining = None
    if user_profile.deletion_requested:
        delta = user_profile.deletion_requested + timezone.timedelta(days=30) - timezone.now()
        days_remaining = max(0, delta.days)
    
    return render(request, 'delete_account.html', {
        'user_profile': user_profile,
        'days_remaining': days_remaining
    })

def my_classes(request):
    return render(request, 'my_class.html')

def my_exercises(request):
    return render(request, 'my_exercise.html')

def my_quizzes(request):
    return render(request, 'my_quizz.html')

def generate_otp():
    """Generate a 6-digit OTP."""
    return random.randint(100000, 999999)

def send_otp_email(user, otp):
    email_subject = "Your OTP Code"
    
    html_message = render_to_string('emailotp.html', {
        'lastname': user.last_name,
        'otp': otp,
    })
    
    text_message = strip_tags(html_message)

    email = EmailMultiAlternatives(
        email_subject,
        text_message,
        settings.EMAIL_HOST_USER,
        [user.email],
    )
    
    email.attach_alternative(html_message, "text/html")
    
    try:
        email.send(fail_silently=False)
    except BadHeaderError:
        return False
    return True

def user_register(request):
    if request.method == 'POST':
        studentID = request.POST['studentID']
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        birthday = request.POST['birthday']  # This will be a string
        gender = request.POST['gender']
        email = request.POST['email']
        password = request.POST['password']
        cpassword = request.POST['cpassword']

        # Convert birthday string to date
        try:
            birthday_date = datetime.strptime(birthday, "%Y-%m-%d").date()  # Assuming input format is 'YYYY-MM-DD'
        except ValueError:
            messages.error(request, "Invalid birthday format. Please use YYYY-MM-DD.")
            return redirect('register')
        
        # Check if the student exists
        student_list = StudentList.objects.filter(studentID=studentID, birthday=birthday_date).first()

        if student_list:
    # If both studentID and birthday match, proceed with registration
            #messages.success(request, "Student exists, proceeding with registration.")
            pass
        else:
            messages.error(request, "Student does not exist!")
            return redirect('register')

        # Check password match
        if password != cpassword:
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        # Create the user
        try:
            user = User.objects.create_user(
                username=email, email=email, password=password, first_name=firstname, last_name=lastname
            )
            user.is_active = False
            user.save()

            otp = generate_otp()  # Ensure this function is defined in your code
            email_sent = send_otp_email(user, otp)  # Ensure this function is defined

            if not email_sent:
                messages.error(request, "Error sending OTP email. Please try again.")
                return redirect('register')

            # Store registration data in the session, convert birthday to string
            request.session['registration_data'] = {
                'user_id': user.id,
                'studentID': studentID,
                'firstname': firstname,
                'lastname': lastname,
                'birthday': birthday_date.isoformat(),  # Convert date to string
                'gender': gender,
                'role': 'Student',
                'otp': otp,
            }

            messages.success(request, 'OTP has been sent to your email. Please verify your account.')
            return redirect('verify_otp')

        except Exception as e:
            messages.error(request, f"Registration failed: {e}")
            return redirect('register')

    return render(request, 'register.html')

def verify_otp(request):
    if request.method == 'POST':
        input_otp = request.POST['otp']
        session_data = request.session.get('registration_data')

        if session_data and input_otp == str(session_data['otp']):
            user = User.objects.get(id=session_data['user_id'])
            user_profile = UserProfile.objects.create(
                user=user,
                studentID=session_data['studentID'],
                firstname=session_data['firstname'],
                lastname=session_data['lastname'],
                birthday=session_data['birthday'],
                gender=session_data['gender'],
                role=session_data['role']
            )

            user.is_active = True 
            user.save()

            del request.session['registration_data']
            messages.success(request, 'Your account has been verified and registered successfully!')
            return redirect('login')
        else:
            messages.error(request, 'Invalid OTP. Please try again.')
            return redirect('verify_otp')

    return render(request, 'verification.html')

def user_login(request):
    if request.method == 'POST':
        login_input = request.POST['email']
        password = request.POST['password']

        try:
            user = User.objects.get(Q(email=login_input) | Q(username=login_input))
            username = user.username
            
            # Check if user has a pending deletion and cancel it
            try:
                profile = user.userprofile
                if profile.is_deleted:
                    profile.cancel_deletion()
                    messages.success(request, 'Welcome back! Your account deletion has been cancelled.')
            except UserProfile.DoesNotExist:
                pass

        except User.DoesNotExist:
            username = None

        if username is not None:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                
                # Create different log messages for admin and regular users
                if user.is_staff:
                    UserActivity.objects.create(
                        user=user,
                        activity_type="admin_login",
                        description=f"Admin {user.username} logged in"
                    )
                    messages.success(request, "Admin login successful.")
                    return redirect('admin-page')
                else:
                    UserActivity.objects.create(
                        user=user,
                        activity_type="user_login",
                        description=f"User {user.username} logged in"
                    )
                    messages.success(request, "Login successful.")
                    return redirect('home')
            else:
                messages.error(request, "Invalid credentials.")
        else:
            messages.error(request, "No account found with the provided credentials.")
        return redirect('login')

    return render(request, 'login.html')

def user_logout(request):
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('login')

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        try:
            user = User.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))  # Removed .decode()

            email_subject = "Reset Your Password"
            email_template = 'emailfpass.html'
            email_context = {
                'email': user.email,
                'domain': request.get_host(),
                'uid': uid,
                'token': token,
            }
            email_message = render_to_string(email_template, email_context)
            email = EmailMessage(email_subject, email_message, settings.DEFAULT_FROM_EMAIL, [user.email])
            email.content_subtype = "html"
            email.send(fail_silently=False)
            
            messages.success(request, "Password reset link has been sent to your email.")
            return redirect('forgot-password')

        except User.DoesNotExist:
            messages.error(request, "Email not found.")
            return redirect('forgot-password')

    return render(request, 'forgot-password.html')

def reset_password(request):
    if request.method == 'GET':
        uidb64 = request.GET.get('uid')
        token = request.GET.get('token')

        print(f"uidb64: {uidb64}, token: {token}")  # Debugging output

        if uidb64 is None or token is None:
            messages.error(request, "Invalid password reset link.")
            return redirect('forgot-password')

        try:
            # Decode the uidb64 to get the user ID
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
            print(f"User found: {user}")  # Debugging output

            # Render the reset password template
            return render(request, 'reset-password.html', {'uid': uid, 'token': token})

        except (TypeError, ValueError, User.DoesNotExist):
            messages.error(request, "Invalid password reset link.")
            return redirect('forgot-password')

    elif request.method == 'POST':
        uid = request.POST['uid']
        token = request.POST['token']
        password = request.POST['password']
        cpassword = request.POST['cpassword']

        # Check if passwords match
        if password != cpassword:
            messages.error(request, "Passwords do not match.")
            return render(request, 'reset-password.html', {'uid': uid, 'token': token})

        try:
            # Verify the user using uid and token
            user = User.objects.get(pk=uid)

            if default_token_generator.check_token(user, token):
                user.set_password(password)  # Set the new password
                user.save()  # Save the user with the new password
                messages.success(request, "Your password has been reset successfully! You can now log in.")
                return redirect('login')
            else:
                messages.error(request, "Invalid password reset link.")
                return redirect('forgot-password')

        except User.DoesNotExist:
            messages.error(request, "Invalid password reset link.")
            return redirect('forgot-password')

    # If neither GET nor POST, render the reset password page
    return render(request, 'reset-password.html') 

@login_required(login_url='login')
def admin_page(request):
    # Check if user is admin/staff
    if not request.user.is_staff:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('home')

    # Count instructors and students
    counts = UserProfile.objects.values('role').annotate(count=Count('role')).order_by('role')
    instructor_count = next((item['count'] for item in counts if item['role'] == 'Instructor'), 0)
    student_count = next((item['count'] for item in counts if item['role'] == 'Student'), 0)

    # Calculate total users
    total_users = instructor_count + student_count

    # Fetch recent students (adjust limit as needed, e.g., last 5 students)
    new_students = UserProfile.objects.filter(role='Student').order_by('-user__date_joined')[:5]

    # Fetch recent activity logs (last 10 entries) - only for admin users
    recent_logs = UserActivity.objects.filter(
        user__is_staff=True,  # Only get logs created by admin users
        activity_type__in=[
            'admin_login',  # Added admin_login to the list
            'instructor_creation',
            'instructor_edit',
            'instructor_deletion',
            'student_account_edit',
            'student_deletion'
        ]
    ).select_related('user').order_by('-date')[:10]

    # Prepare context for the template
    context = {
        'instructor_count': instructor_count,
        'student_count': student_count,
        'total_users': total_users,
        'new_students': new_students,
        'recent_logs': recent_logs,
    }

    return render(request, 'admin_page/index.html', context)

def instructor_list(request):
    instructors = UserProfile.objects.filter(role='Instructor')
    return render(request, 'admin_page/tables/instructor_table.html', {'instructors': instructors})

def student_list(request):
    students = UserProfile.objects.filter(role='Student')
    return render(request, 'admin_page/tables/student_table.html', {'students': students})

@login_required(login_url='login')
def student_view(request, pk):
    # Activate Manila timezone
    activate(pytz.timezone('Asia/Manila'))
    
    student = get_object_or_404(UserProfile, pk=pk, role='Student')
    activities = student.user.useractivity_set.all()[:10]
    
    context = {
        'student': student,
        'activities': activities,
        'timezone': timezone.get_current_timezone_name()
    }
    return render(request, 'admin_page/forms/student_view.html', context)

@login_required(login_url='login')
def student_edit(request, pk):
    student = get_object_or_404(UserProfile, pk=pk, role='Student')
    
    if request.method == 'POST':
        try:
            # Get form data
            username = request.POST['username']
            email = request.POST['email']
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            # Check if username is already taken by another user
            if User.objects.exclude(pk=student.user.pk).filter(username=username).exists():
                messages.error(request, 'Username is already taken.')
                return redirect('student-edit', pk=pk)

            # Check if email is already taken by another user
            if User.objects.exclude(pk=student.user.pk).filter(email=email).exists():
                messages.error(request, 'Email is already taken.')
                return redirect('student-edit', pk=pk)

            # Update user information
            student.user.username = username
            student.user.email = email

            # Update password if provided
            if new_password:
                if new_password != confirm_password:
                    messages.error(request, 'Passwords do not match.')
                    return redirect('student-edit', pk=pk)
                student.user.set_password(new_password)

            student.user.save()

            # Log the activity
            UserActivity.objects.create(
                user=request.user,
                activity_type='student_account_edit',
                description=f'Updated account information for student {student.firstname} {student.lastname}'
            )

            messages.success(request, 'Student account information updated successfully!')
            return redirect('student-list')

        except Exception as e:
            messages.error(request, f'Error updating student account: {str(e)}')
            return redirect('student-edit', pk=pk)

    return render(request, 'admin_page/forms/student_edit.html', {'student': student})

def student_delete(request, pk):
    if request.method == 'POST':
        student = get_object_or_404(UserProfile, pk=pk, role='Student')
        try:
            student_name = f"{student.firstname} {student.lastname}"
            
            # Create activity log before deleting
            create_activity(
                user=request.user,
                activity_type='student_deletion',
                description=f'Deleted student account for {student_name}'
            )
            
            # Delete the user (this will cascade delete the UserProfile)
            student.user.delete()
            
            messages.success(request, 'Student deleted successfully!')
        except Exception as e:
            messages.error(request, f'Error deleting student: {str(e)}')
    
    return redirect('student-list')

def send_instructor_credentials(user, password):
    """Send email with login credentials to new instructor."""
    email_subject = "Your Instructor Account Credentials"
    
    html_message = render_to_string('admin_page/emails/instructor_credentials.html', {
        'firstname': user.first_name,
        'lastname': user.last_name,
        'username': user.username,
        'email': user.email,
        'password': password,
    })
    
    text_message = strip_tags(html_message)

    email = EmailMultiAlternatives(
        email_subject,
        text_message,
        settings.EMAIL_HOST_USER,
        [user.email],
    )
    
    email.attach_alternative(html_message, "text/html")
    
    try:
        email.send(fail_silently=False)
        return True
    except BadHeaderError:
        return False

@login_required(login_url='login')
def instructor_form(request):
    if request.method == 'POST':
        try:
            # Get form data for User model
            username = request.POST['username']
            email = request.POST['email']
            password = request.POST['password']
            
            # Get form data for UserProfile model
            firstname = request.POST['firstname']
            lastname = request.POST['lastname']
            studentID = request.POST.get('studentID')
            birthday = request.POST['birthday']
            gender = request.POST['gender']
            bio = request.POST.get('bio', '')
            display_photo = request.FILES.get('display_photo')

            # Validate that username/email doesn't already exist
            if User.objects.filter(Q(username=username) | Q(email=email)).exists():
                messages.error(request, 'Username or email already exists.')
                return redirect('instructor_form')

            # Create User account
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=firstname,
                last_name=lastname
            )

            # Create UserProfile for instructor
            profile = UserProfile.objects.create(
                user=user,
                studentID=studentID,
                firstname=firstname,
                lastname=lastname,
                birthday=birthday,
                gender=gender,
                role='Instructor',
                bio=bio
            )

            # Handle profile picture if uploaded
            if display_photo:
                profile.display_photo = display_photo
                profile.save()

            # Send credentials email
            email_sent = send_instructor_credentials(user, password)
            if not email_sent:
                messages.warning(request, 'Instructor account created but failed to send email notification.')

            # Log the activity
            UserActivity.objects.create(
                user=request.user,
                activity_type='instructor_creation',
                description=f'Created new instructor account for {username}'
            )

            messages.success(request, 'Instructor added successfully!')
            return redirect('instructor-list')

        except Exception as e:
            messages.error(request, f'Error adding instructor: {str(e)}')
            return redirect('instructor-form')

    return render(request, 'admin_page/forms/instructor_form.html')

@login_required(login_url='login')
def ctu_student_list(request):
    # Get all students from StudentList model, ordered by studentID
    students = StudentList.objects.all().order_by('studentID')
    
    # Pass the students to the template
    context = {
        'students': students
    }
    return render(request, 'admin_page/tables/ctu_student_table.html', context)

"""@login_required(login_url='login')
def student_form(request):
    if request.method == 'POST':    
        try:
            # Get form data
            studentID = request.POST['studentID']
            firstname = request.POST['firstname']
            lastname = request.POST['lastname']
            birthday = request.POST['birthday']

            # Create new student in StudentList
            student = StudentList.objects.create(
                studentID=studentID,
                firstname=firstname,
                lastname=lastname,
                birthday=birthday
            )

            # Log the activity
            UserActivity.objects.create(
                user=request.user,
                activity_type='student_creation',
                description=f'Added new student {firstname} {lastname} to CTU Student List'
            )

            messages.success(request, 'Student added successfully!')
            return redirect('ctu-student-list')

        except Exception as e:
            messages.error(request, f'Error adding student: {str(e)}')
            return redirect('student-form')

    return render(request, 'admin_page/forms/student_form.html')"""

def create_activity(user, activity_type, description):
    manila_tz = pytz.timezone('Asia/Manila')
    current_time = timezone.now().astimezone(manila_tz)
    
    UserActivity.objects.create(
        user=user,
        activity_type=activity_type,
        date=current_time,
        description=description
    )

@login_required(login_url='login')
def instructor_view(request, pk):
    instructor = get_object_or_404(UserProfile, pk=pk, role='Instructor')
    return render(request, 'admin_page/forms/instructor_view.html', {'instructor': instructor})

@login_required(login_url='login')
def instructor_edit(request, pk):
    instructor = get_object_or_404(UserProfile, pk=pk, role='Instructor')
    
    if request.method == 'POST':
        try:
            # Get form data
            username = request.POST['username']
            email = request.POST['email']
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            # Check if username is already taken by another user
            if User.objects.exclude(pk=instructor.user.pk).filter(username=username).exists():
                messages.error(request, 'Username is already taken.')
                return redirect('instructor-edit', pk=pk)

            # Check if email is already taken by another user
            if User.objects.exclude(pk=instructor.user.pk).filter(email=email).exists():
                messages.error(request, 'Email is already taken.')
                return redirect('instructor-edit', pk=pk)

            # Update user information
            instructor.user.username = username
            instructor.user.email = email

            # Update password if provided
            if new_password:
                if new_password != confirm_password:
                    messages.error(request, 'Passwords do not match.')
                    return redirect('instructor-edit', pk=pk)
                instructor.user.set_password(new_password)

            instructor.user.save()

            # Log the activity
            create_activity(
                user=request.user,
                activity_type='instructor_edit',
                description=f'Updated instructor account for {instructor.firstname} {instructor.lastname}'
            )

            messages.success(request, 'Instructor account updated successfully!')
            return redirect('instructor-list')

        except Exception as e:
            messages.error(request, f'Error updating instructor account: {str(e)}')
            return redirect('instructor-edit', pk=pk)

    return render(request, 'admin_page/forms/instructor_edit.html', {'instructor': instructor})

@login_required(login_url='login')
def instructor_delete(request, pk):
    if request.method == 'POST':
        instructor = get_object_or_404(UserProfile, pk=pk, role='Instructor')
        try:
            instructor_name = f"{instructor.firstname} {instructor.lastname}"
            
            # Create activity log before deleting
            create_activity(
                user=request.user,
                activity_type='instructor_deletion',
                description=f'Deleted instructor account for {instructor_name}'
            )
            
            # Delete the user (this will cascade delete the UserProfile)
            instructor.user.delete()
            
            messages.success(request, 'Instructor deleted successfully!')
        except Exception as e:
            messages.error(request, f'Error deleting instructor: {str(e)}')
    
    return redirect('instructor-list')

@login_required(login_url='login')
def change_photo(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    if request.method == 'POST':
        if 'display_photo' in request.FILES:
            user_profile.display_photo = request.FILES['display_photo']
            user_profile.save()
            messages.success(request, 'Profile photo updated successfully!')
            return redirect('edit_profile')
    
    return render(request, 'change_photo.html', {'user_profile': user_profile})

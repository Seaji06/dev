from django.shortcuts import render, redirect
import pyrebase, logging
from django.contrib import messages
from django.core.mail import send_mail
import random

# Firebase configuration
config = {
    "apiKey": "AIzaSyAqy5Qbf7c6eOyB65AVYqbagVh7dbeWlNM",
    "authDomain": "coding-nexus-a0713.firebaseapp.com",
    "databaseURL": "https://coding-nexus-a0713-default-rtdb.asia-southeast1.firebasedatabase.app",
    "projectId": "coding-nexus-a0713",
    "storageBucket": "coding-nexus-a0713.appspot.com",
    "messagingSenderId": "757069789705",
    "appId": "1:757069789705:web:0e0182530be7d353e156d8",
}

firebase = pyrebase.initialize_app(config)
authe = firebase.auth()
database = firebase.database()

def generate_otp():
    """Generate a 6-digit OTP."""
    return random.randint(100000, 999999)

def send_otp_email(email, otp):
    """Send the OTP code to the user's email."""
    send_mail(
        'Your OTP Code',
        f'Your OTP code is {otp}.',
        'your-email@example.com',  # Replace with your email
        [email],
        fail_silently=False,
    )

def home(request):
    if 'uid' in request.session:
        # User is logged in
        return render(request, 'index.html', {'logged_in': True})
    else:
        # User is not logged in
        return render(request, 'index.html', {'logged_in': False})

def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            # Log in user using Firebase Authentication
            user = authe.sign_in_with_email_and_password(email, password)
            session_id = user['idToken']  # Firebase session token
            request.session['uid'] = str(session_id)  # Store the session token
            
            return redirect('home')  # Redirect to the home page upon successful login

        except Exception as e:
            # Handle login error and display a user-friendly error message
            error_message = str(e)
            messages.error(request, "Invalid email or password. Please try again.")
            return render(request, 'login.html')

    return render(request, 'login.html')

def user_register(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            # Generate OTP
            otp = generate_otp()
            request.session['otp'] = otp
            request.session['otp_email'] = email

            # Send OTP email
            send_otp_email(email, otp)

            # Redirect to OTP verification page
            messages.success(request, 'OTP sent to your email. Please verify.')
            return redirect('verify_otp')

        except Exception as e:
            error_message = str(e)
            if "WEAK_PASSWORD" in error_message:
                user_friendly_message = "Your password must be at least 6 characters long."
            elif "EMAIL_EXISTS" in error_message:
                user_friendly_message = "An account with this email already exists."
            elif "INVALID_EMAIL" in error_message:
                user_friendly_message = "The email address is not valid."
            else:
                user_friendly_message = "An error occurred. Please try again."

            logging.error(f"Error during registration: {error_message}")
            messages.error(request, user_friendly_message)
            return render(request, 'register.html')

    return render(request, 'register.html')

def verify_otp(request):
    if request.method == 'POST':
        otp = request.POST.get('otp')
        correct_otp = str(request.session.get('otp'))

        if otp == correct_otp:
            email = request.session.get('otp_email')
            password = request.POST.get('password')

            try:
                # Create user using Firebase Authentication
                user = authe.create_user_with_email_and_password(email, password)
                uid = user['localId']

                # Store user email in Firebase Realtime Database
                data = {
                    "email": email,
                }
                database.child("users").child(uid).set(data)

                messages.success(request, 'Account created successfully! Please login.')
                return redirect('login')

            except Exception as e:
                error_message = str(e)
                if "WEAK_PASSWORD" in error_message:
                    user_friendly_message = "Your password must be at least 6 characters long."
                elif "EMAIL_EXISTS" in error_message:
                    user_friendly_message = "An account with this email already exists."
                elif "INVALID_EMAIL" in error_message:
                    user_friendly_message = "The email address is not valid."
                else:
                    user_friendly_message = "An error occurred. Please try again."

                logging.error(f"Error during registration: {error_message}")
                messages.error(request, user_friendly_message)
                return render(request, 'verify_otp.html')

        else:
            messages.error(request, 'Invalid OTP. Please try again.')
            return render(request, 'verify_otp.html')

    return render(request, 'verify_otp.html')

def user_logout(request):
    try:
        del request.session['uid']  # Delete session
        messages.success(request, 'Logged out successfully!')
    except KeyError:
        pass
    return redirect('login')

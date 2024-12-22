from django.shortcuts import render, redirect
from django.contrib.auth import authenticate,logout
from django.contrib.auth import login as auth_login
from django.contrib import messages
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta,datetime
from .models import User
from django.conf import settings
import random
import string
from product.models import Product
import re
from django.utils.timezone import now








def generate_otp():
    return ''.join(random.choices(string.digits, k=6))



def signup(request):
    form_errors = {}
    
    if request.method == 'POST':
        email = request.POST.get('email')
        username = request.POST.get('username').strip()
        phone_number = request.POST.get('phone')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        
        if not email or not username or not password or not confirm_password:
            form_errors['general'] = "Email, username, password, and confirm password are required."
        else:
            if not re.match("^[A-Za-z0-9]*$", username):
                form_errors['username'] = "Username must contain only alphanumeric characters (no special characters)."
            
            if not email.__contains__('@'):
                form_errors['email'] = "Please enter a valid email address."
            

            if not phone_number.isdigit():
                form_errors['phone'] = "Phone number must contain only numbers."

            elif len(phone_number)<10 or len(phone_number)>10:
                form_errors['phone'] = "Phone number must be 10"


            
            if len(password) < 8:
                form_errors['password'] = "Password must be at least 8 characters long."
            
            elif not any(char.isupper() for char in password):
                form_errors['password'] = "Password must contain at least one uppercase letter."
                
            elif not any(char.islower() for char in password):
                form_errors['password'] = "Password must contain at least one lowercase letter."
                
            elif not any(char.isdigit() for char in password):
                form_errors['password'] = "Password must contain at least one number."
                
            elif not any(char in "!@#$%^&*()_+-=[]{}|;:,.<>?" for char in password):
                form_errors['password'] = "Password must contain at least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)"
                
            elif password != confirm_password:
                form_errors['password'] = "Passwords do not match."


            
            if User.objects.filter(email=email).exists():
                form_errors['email'] = "Email is already taken."
            
            if User.objects.filter(username=username).exists():
                form_errors['username'] = "Username is already taken."

           
            if not form_errors:
                
                otp = generate_otp()
                otp_expiry = (timezone.now() + timedelta(minutes=1)).isoformat() 

                request.session['user_data'] = {
                    'email': email,
                    'username': username,
                    'phone_number': phone_number,
                    'password': password,
                    'otp': otp,
                    'otp_expiry': otp_expiry
                }

                request.session.save()

                
                send_mail(
                        'Your OTP Code',
                        f'Your OTP is: {otp}',
                        settings.DEFAULT_FROM_EMAIL, 
                        [email], 
                    )

                print(otp)

               
                return redirect('verify_email')

        
        return render(request, 'user_side/signup.html', {'form_errors': form_errors})

    return render(request, 'user_side/signup.html')





from django.contrib.auth.hashers import make_password
from django.utils.dateparse import parse_datetime


def verify_email(request):
    user_data = request.session.get('user_data')
    if not user_data:
        messages.error(request, "Session expired or user not found. Please sign up again.")
        return redirect('signup')

    otp_expiry_str = user_data.get('otp_expiry')
    if not otp_expiry_str:
        messages.error(request, "Invalid session data. Please sign up again.")
        return redirect('signup')

    otp_expiry = parse_datetime(otp_expiry_str)

    if request.method == 'POST':
        otp_entered = request.POST.get('otp')

        if not otp_entered:
            messages.error(request, "OTP is required.")
            return render(request, 'user_side/verify_otp.html')

        current_time = now()

        if current_time > otp_expiry:
            messages.error(request, "OTP has expired. Please request a new one.")
            return redirect('resend_otp')

        if otp_entered == user_data['otp']:
            User.objects.create(
                email=user_data['email'],
                username=user_data['username'],
                phone_number=user_data['phone_number'],
                password=make_password(user_data['password']),
                is_active=True
            )
            messages.success(request, "Account verified successfully.")
            return redirect('login')

        messages.error(request, "Invalid OTP. Please try again.")
        return render(request, 'user_side/verify_otp.html')

    return render(request, 'user_side/verify_otp.html')






def resend_otp(request):
    print('hello')
    user_data = request.session.get('user_data')
    if not user_data:
        messages.error(request, "Session expired or user not found. Please sign up again.")
        return redirect('signup')

    otp = generate_otp()
    print(otp)
    otp_expiry = timezone.now() + timedelta(minutes=5)  

    user_data.update({
        'otp': otp,
        'otp_expiry': otp_expiry.isoformat()
    })
    request.session['user_data'] = user_data  

    try:
        send_mail(
            'Your New OTP Code',
            f'Your OTP is: {otp}',
            settings.DEFAULT_FROM_EMAIL,
            [user_data['email']],
        )
    except Exception as e:
        messages.error(request, "Failed to send email. Please try again later.")
        return redirect('verify_email')

    messages.success(request, "A new OTP has been sent to your email.")
    return redirect('verify_email')

    






def login_view(request):
    if request.method == "POST":
        
        email = request.POST.get("email")
        password = request.POST.get("password")
        if not email or not password:
            messages.error(request, "Please type email and password")
            return redirect('login')
        user = authenticate(request, email=email, password=password)

        if user is not None:
            if user.is_active:
                auth_login(request, user)
                messages.success(request, "You are logged in.")
                return redirect('home')
            else:
                messages.error(request, "Your account is not activated.")
        else:
            messages.error(request, "Invalid email or password. Please try again.")

    return render(request, "user_side/login.html")

    





def home(request):
    products = Product.objects.filter(is_delete=False)[:8]
    return render(request, 'user_side/index.html',{'products':products})




def user_logout(request):
    logout(request)
    messages.success(request,'You have sucessfully logged out')
    return redirect('home') 
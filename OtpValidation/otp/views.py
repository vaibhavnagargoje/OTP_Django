import random
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.utils import timezone
from .models import TemporaryUser
from django.contrib.auth.models import User


# Create your views here.

def home(request):
    return render(request,'home.html')

def CustomLogin(request):
    
    return render(request,'login.html')






# Generate a 6-digit OTP
def generate_otp():
    return str(random.randint(100000, 999999))

def register(request):
    if request.method == 'POST':
        email = request.POST['email']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email is already registered. Please log in.')
            return redirect('login')


        otp = generate_otp()
        
        # Save temporary user
        # TemporaryUser.objects.create(email=email, first_name=first_name, last_name=last_name, otp=otp)
        
        temp_user, created = TemporaryUser.objects.update_or_create(
            email=email,
            defaults={
                'otp': otp,
                'first_name': first_name,
                'last_name': last_name,
                'otp_created_at': timezone.now()
            }
        )



        # Send OTP via email
        send_mail(
            'Your OTP Code',
            f'Your OTP code is {otp}',
            'noreply@yourdomain.com',
            [email],
            fail_silently=False,
        )


        # Store the email in the session
        request.session['temp_email'] = email


        messages.success(request, 'OTP sent to your email. Please verify.')
        return redirect('verify_otp')
    
    return render(request, 'register.html')




def verify_otp(request):
    temp_email = request.session.get('temp_email')
    if not temp_email:
        messages.error(request, 'Session expired. Please try registering again.')
        return redirect('register')

    if request.method == 'POST':
        otp = request.POST['otp']
        temp_user = TemporaryUser.objects.filter(email=temp_email, otp=otp).first()
        
        if temp_user and (timezone.now() - temp_user.otp_created_at).seconds < 300:  # OTP valid for 5 minutes
            # Create a new User object
            user = User.objects.create_user(email=temp_user.email, username=temp_user.email, first_name=temp_user.first_name, last_name=temp_user.last_name)
            user.set_unusable_password()  # Set a dummy password or handle password setting in another flow
            user.save()
            
            # Delete temporary user
            temp_user.delete()
            
            # Log the user in
            login(request, user)
            
            # Redirect to success page
            return redirect('registration_success')
        else:
            messages.error(request, 'Invalid OTP or OTP expired.')
            return redirect('verify_otp')
    
    return render(request, 'verify_otp.html')



def registration_success(request):

    return render(request, 'registration_success.html')
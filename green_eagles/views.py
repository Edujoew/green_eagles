from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ContactForm
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import MemberProfile

# Create your views here.
def home(request):
    return render(request, 'green_eagles/home.html')

def about(request):
    return render(request, 'green_eagles/about.html')

def contact(request):
    return render(request, 'green_eagles/contact.html')

def services(request):
    return render(request, 'green_eagles/services.html')

def faq(request):
    return render(request, 'green_eagles/faq.html')

def green_eagles_crew(request):
    return render(request, 'green_eagles/green_eagles_crew.html')

def messengers_of_peace(request):
    return render(request, 'green_eagles/messengers_of_peace.html')

def gallery(request):
    return render(request, 'green_eagles/gallery.html')

# Contact form view
def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        # Clean, professional email formatting
        full_message = (
            f"Sender Name: {name}\n"
            f"Sender Email: {email}\n"
            f"Subject: {subject}\n\n"
            f"Message:\n{message}"
        )

        recipient_list = ['plastout.org@gmail.com']

        try:
            send_mail(
                subject=f"{name}: {subject}",
                message=full_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipient_list,
                fail_silently=False,
            )
            messages.success(request, 'Thank you! Your message has been sent successfully to PLASTOUT.')
        except Exception as e:
            messages.error(request, 'There was an issue sending your message. Please try again later.')

        return redirect('green_eagles:contact')

    return render(request, 'green_eagles/contact.html')


def register_member(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        wing = request.POST.get('wing', 'GE')
        phone = request.POST.get('phone', '')

        if form.is_valid():
            user = form.save()
            # Create associated profile
            MemberProfile.objects.create(user=user, wing=wing, phone=phone)
            login(request, user)
            messages.success(request, 'Welcome to PLASTOUT! Your account was created successfully.')
            return redirect('green_eagles:dashboard')
    else:
        form = UserCreationForm()

    return render(request, 'green_eagles/register.html', {'form': form})

def login_member(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('green_eagles:dashboard')
    else:
        form = AuthenticationForm()

    return render(request, 'green_eagles/login.html', {'form': form})

def logout_member(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('green_eagles:login')

@login_required
def dashboard(request):
    profile, _ = MemberProfile.objects.get_or_create(user=request.user)
    return render(request, 'green_eagles/dashboard.html', {'profile': profile})

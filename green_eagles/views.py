from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required

from .models import MemberProfile, GalleryItem
from .forms import ContactForm, GalleryItemForm


def home(request):
    return render(request, 'green_eagles/home.html')


def about(request):
    return render(request, 'green_eagles/about.html')


def services(request):
    return render(request, 'green_eagles/services.html')


def faq(request):
    return render(request, 'green_eagles/faq.html')


def green_eagles_crew(request):
    return render(request, 'green_eagles/green_eagles_crew.html')


def messengers_of_peace(request):
    return render(request, 'green_eagles/messengers_of_peace.html')


def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

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
        except Exception:
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


# GALLERY VIEWS

def gallery(request):
    photos = GalleryItem.objects.all().order_by('-created_at')
    return render(request, 'green_eagles/gallery.html', {'photos': photos})


def gallery_create(request):
    if request.method == 'POST':
        form = GalleryItemForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Image added successfully!')
            return redirect('green_eagles:gallery')
    else:
        form = GalleryItemForm()
    return render(request, 'green_eagles/gallery_form.html', {'form': form, 'title': 'Add New Picture'})


def gallery_update(request, pk):
    photo = get_object_or_404(GalleryItem, pk=pk)
    if request.method == 'POST':
        form = GalleryItemForm(request.POST, request.FILES, instance=photo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Image updated successfully!')
            return redirect('green_eagles:gallery')
    else:
        form = GalleryItemForm(instance=photo)
    return render(request, 'green_eagles/gallery_form.html', {'form': form, 'title': 'Edit Picture', 'photo': photo})


def gallery_delete(request, pk):
    photo = get_object_or_404(GalleryItem, pk=pk)
    if request.method == 'POST':
        photo.image.delete(save=False)
        photo.delete()
        messages.success(request, 'Image deleted successfully!')
        return redirect('green_eagles:gallery')
    return render(request, 'green_eagles/gallery_confirm_delete.html', {'photo': photo})
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from .models import Announcement
from .forms import AnnouncementForm

from .models import MemberProfile, GalleryItem
from .forms import ContactForm, GalleryItemForm, UserUpdateForm, MemberProfileUpdateForm


def home(request):
    return render(request, 'green_eagles/home.html')


def about(request):
    return render(request, 'green_eagles/about.html')


def services(request):
    return render(request, 'green_eagles/services.html')


def faq(request):
    return render(request, 'green_eagles/faq.html')


# --- GREEN EAGLES CREW WING VIEWS (Separate HTML files) ---
def green_eagles_crew(request):
    return render(request, 'green_eagles/crew/home.html')

def crew_about(request):
    return render(request, 'green_eagles/crew/about.html')

def crew_activities(request):
    return render(request, 'green_eagles/crew/activities.html')

def crew_gallery(request):
    return render(request, 'green_eagles/crew/gallery.html')

def crew_faq(request):
    return render(request, 'green_eagles/crew/faq.html')


# --- MESSENGERS OF PEACE WING VIEWS (Separate HTML files) ---
def messengers_of_peace(request):
    return render(request, 'green_eagles/mop/home.html')

def mop_about(request):
    return render(request, 'green_eagles/mop/about.html')

def mop_activities(request):
    return render(request, 'green_eagles/mop/activities.html')

def mop_gallery(request):
    return render(request, 'green_eagles/mop/gallery.html')

def mop_faq(request):
    return render(request, 'green_eagles/mop/faq.html')


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


@login_required
def edit_profile(request):
    profile, _ = MemberProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = MemberProfileUpdateForm(request.POST, instance=profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('green_eagles:dashboard')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = MemberProfileUpdateForm(instance=profile)

    context = {
        'u_form': u_form,
        'p_form': p_form,
        'profile': profile,
    }
    return render(request, 'green_eagles/edit_profile.html', context)


# ADMIN MEMBER MANAGEMENT VIEWS

def superuser_required(user):
    return user.is_active and user.is_superuser


def is_wing_admin(user):
    """Allows Superusers, Executive Admins, or Wing Coordinators to access admin tools."""
    if not user.is_active:
        return False
    if user.is_superuser:
        return True
    profile = getattr(user, 'profile', None)
    return profile and profile.role in ['EXEC', 'COORDINATOR']


@user_passes_test(is_wing_admin)
def manage_members(request):
    user = request.user
    profile = getattr(user, 'profile', None)

    if user.is_superuser or (profile and profile.role == 'EXEC'):
        members = User.objects.select_related('profile').all().order_by('-date_joined')
    elif profile and profile.role == 'COORDINATOR':
        if profile.wing == 'BOTH':
            members = User.objects.select_related('profile').all().order_by('-date_joined')
        else:
            members = User.objects.select_related('profile').filter(profile__wing=profile.wing).order_by('-date_joined')
    else:
        members = User.objects.none()

    return render(request, 'green_eagles/admin_manage_members.html', {'members': members})


@user_passes_test(is_wing_admin)
def admin_add_member(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        wing = request.POST.get('wing', 'GE')
        phone = request.POST.get('phone', '')
        if form.is_valid():
            user = form.save()
            MemberProfile.objects.create(user=user, wing=wing, phone=phone)
            messages.success(request, f'Member "{user.username}" added successfully.')
            return redirect('green_eagles:admin_manage_members')
    else:
        form = UserCreationForm()
    return render(request, 'green_eagles/admin_add_member.html', {'form': form})


@user_passes_test(is_wing_admin)
def admin_edit_member(request, pk):
    member = get_object_or_404(User, pk=pk)
    profile, _ = MemberProfile.objects.get_or_create(user=member)

    # Wing coordinators can only edit members belonging to their wing (unless EXEC/Superuser)
    user_profile = getattr(request.user, 'profile', None)
    if not request.user.is_superuser and user_profile and user_profile.role == 'COORDINATOR':
        if user_profile.wing != 'BOTH' and profile.wing != user_profile.wing:
            messages.error(request, "You can only edit members within your assigned wing.")
            return redirect('green_eagles:admin_manage_members')

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=member)
        p_form = MemberProfileUpdateForm(request.POST, instance=profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Updated profile for "{member.username}".')
            return redirect('green_eagles:admin_manage_members')
    else:
        u_form = UserUpdateForm(instance=member)
        p_form = MemberProfileUpdateForm(instance=profile)

    return render(request, 'green_eagles/admin_edit_member.html', {
        'member': member,
        'u_form': u_form,
        'p_form': p_form
    })


@user_passes_test(is_wing_admin)
def admin_delete_member(request, pk):
    member = get_object_or_404(User, pk=pk)
    profile = getattr(member, 'profile', None)

    # Wing coordinators can only delete members belonging to their wing
    user_profile = getattr(request.user, 'profile', None)
    if not request.user.is_superuser and user_profile and user_profile.role == 'COORDINATOR':
        if profile and user_profile.wing != 'BOTH' and profile.wing != user_profile.wing:
            messages.error(request, "You can only remove members within your assigned wing.")
            return redirect('green_eagles:admin_manage_members')

    if request.method == 'POST':
        username = member.username
        member.delete()
        messages.success(request, f'Member "{username}" has been permanently removed.')
        return redirect('green_eagles:admin_manage_members')
    return render(request, 'green_eagles/admin_delete_member.html', {'member': member})


@login_required
def dashboard(request):
    profile, _ = MemberProfile.objects.get_or_create(user=request.user)
    
    # Filter announcements based on user's wing or central announcements
    if request.user.is_superuser or (profile and profile.role == 'EXEC'):
        announcements = Announcement.objects.all()[:5]
    elif profile:
        announcements = Announcement.objects.filter(target_wing__in=['ALL', profile.wing])[:5]
    else:
        announcements = Announcement.objects.filter(target_wing='ALL')[:5]
    
    context = {
        'profile': profile,
        'announcements': announcements,
    }
    return render(request, 'green_eagles/dashboard.html', context)


@user_passes_test(is_wing_admin)
def post_announcement(request):
    user_profile = getattr(request.user, 'profile', None)
    
    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.author = request.user
            
            # Restrict wing coordinators from posting outside their wing
            if not request.user.is_superuser and user_profile and user_profile.role == 'COORDINATOR':
                if user_profile.wing != 'BOTH' and announcement.target_wing != 'ALL' and announcement.target_wing != user_profile.wing:
                    announcement.target_wing = user_profile.wing

            announcement.save()
            messages.success(request, 'Announcement published successfully!')
            return redirect('green_eagles:dashboard')
    else:
        form = AnnouncementForm()
    
    return render(request, 'green_eagles/announcement_form.html', {'form': form})


@user_passes_test(is_wing_admin)
def delete_announcement(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk)
    announcement.delete()
    messages.success(request, 'Announcement deleted.')
    return redirect('green_eagles:dashboard')

@login_required
def crew_dashboard(request):
    """Dedicated dashboard for Green Eagles Crew members and admins."""
    profile, _ = MemberProfile.objects.get_or_create(user=request.user)
    announcements = Announcement.objects.filter(target_wing__in=['ALL', 'GE'])[:5]
    
    context = {
        'profile': profile,
        'announcements': announcements,
    }
    return render(request, 'green_eagles/crew/dashboard.html', context)


@login_required
def mop_dashboard(request):
    """Dedicated dashboard for Messengers of Peace members and admins."""
    profile, _ = MemberProfile.objects.get_or_create(user=request.user)
    announcements = Announcement.objects.filter(target_wing__in=['ALL', 'MOP'])[:5]
    
    context = {
        'profile': profile,
        'announcements': announcements,
    }
    return render(request, 'green_eagles/mop/dashboard.html', context)
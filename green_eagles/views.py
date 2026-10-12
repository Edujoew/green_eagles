from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from axes.handlers.proxy import AxesProxyHandler
from functools import wraps
from django_daraja.views import MpesaClient
from .models import Announcement
from .forms import AnnouncementForm

from .models import MemberProfile, GalleryItem
from .forms import ContactForm, GalleryItemForm, UserUpdateForm, MemberProfileUpdateForm


# --- WING ACCESS CONTROL DECORATOR ---
def wing_required(required_wing):
    """
    Restricts access to wing views based on MemberProfile wing choice.
    Allows access if the user's wing is 'BOTH' or matches the required_wing ('GE' or 'MOP').
    Superusers and Executive Admins/Coordinators can also be bypassed or handled if needed.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, "Please log in first to access this wing.")
                return redirect('green_eagles:login')
            
            # Superusers always have full access
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            # Retrieve member profile wing choice
            try:
                profile = request.user.profile
                user_wing = profile.wing
                # Allow EXEC/Superuser roles across wings if applicable
                if profile.role in ['EXEC', 'COORDINATOR'] and profile.wing == 'BOTH':
                    return view_func(request, *args, **kwargs)
            except AttributeError:
                user_wing = 'GE'  # Default fallback if profile is missing

            # Check if user belongs to both or the specific required wing
            if user_wing == 'BOTH' or user_wing == required_wing:
                return view_func(request, *args, **kwargs)

            messages.error(request, "Access denied. You are not registered for this wing.")
            return redirect('green_eagles:dashboard')
            
        return _wrapped_view
    return decorator


def home(request):
    return render(request, 'green_eagles/home.html')


def about(request):
    return render(request, 'green_eagles/about.html')


def services(request):
    return render(request, 'green_eagles/services.html')


def faq(request):
    return render(request, 'green_eagles/faq.html')


# --- GREEN EAGLES CREW WING VIEWS (Restricted to 'GE' or 'BOTH') ---
@wing_required('GE')
def green_eagles_crew(request):
    return render(request, 'green_eagles/crew/home.html')

@wing_required('GE')
def crew_about(request):
    return render(request, 'green_eagles/crew/about.html')

@wing_required('GE')
def crew_activities(request):
    return render(request, 'green_eagles/crew/activities.html')

@wing_required('GE')
def crew_gallery(request):
    return render(request, 'green_eagles/crew/gallery.html')

@wing_required('GE')
def crew_faq(request):
    return render(request, 'green_eagles/crew/faq.html')


# --- MESSENGERS OF PEACE WING VIEWS (Restricted to 'MOP' or 'BOTH') ---
@wing_required('MOP')
def messengers_of_peace(request):
    return render(request, 'green_eagles/mop/home.html')

@wing_required('MOP')
def mop_about(request):
    return render(request, 'green_eagles/mop/about.html')

@wing_required('MOP')
def mop_activities(request):
    return render(request, 'green_eagles/mop/activities.html')

@wing_required('MOP')
def mop_gallery(request):
    return render(request, 'green_eagles/mop/gallery.html')

@wing_required('MOP')
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
        phone_number = request.POST.get('phone_number') or request.POST.get('phone') or ''
        phone_number = ''.join(character for character in phone_number.strip() if character.isdigit())
        if phone_number.startswith('0'):
            phone_number = '254' + phone_number[1:]
        elif len(phone_number) == 9 and phone_number[0] in ('1', '7'):
            phone_number = '254' + phone_number
        paid_amount = int(request.POST.get('payment_amount', 300))

        if form.is_valid():
            user = form.save()
            profile, _ = MemberProfile.objects.get_or_create(user=user)
            profile.wing = wing
            profile.phone = phone or phone_number
            
            # Fee calculation: 300 mandatory registration, remaining amount goes to 200 scarf fee
            scarf_contribution = max(0, paid_amount - 300)
            profile.total_paid = 0
            profile.registration_paid = False
            profile.scarf_balance = max(0, 200 - scarf_contribution)
            profile.save()

            # Trigger M-Pesa STK Push
            if not phone_number:
                messages.warning(request, 'Enter your M-Pesa phone number and click resend on the payment waiting page.')
            else:
                try:
                    # Dynamic account reference based on amount and wing
                    if paid_amount == 300:
                        account_reference = "Green Eagles" if wing == 'GE' else "Messengers"
                    else:
                        account_reference = "Plastout Acct"

                    cl = MpesaClient()
                    stk_response = cl.stk_push(
                        phone_number,
                        paid_amount,
                        account_reference[:12],
                        "PLASTOUT Fee",
                        settings.MPESA_CALLBACK_URL,
                    )
                    if stk_response.response_code == '0':
                        messages.success(request, 'STK Push sent to your phone! Please enter your M-Pesa PIN to complete registration.')
                    else:
                        messages.error(
                            request,
                            stk_response.error_message or stk_response.response_description or 'Daraja STK push failed.',
                        )
                except Exception as e:
                    messages.error(request, f'Payment gateway error: {e}')
            
            # Explicitly set the backend attribute for axes/multiple backends compatibility
            user.backend = 'axes.backends.AxesBackend'
            
            login(request, user)
            return redirect('green_eagles:payment_waiting')
    else:
        form = UserCreationForm()

    return render(request, 'green_eagles/register.html', {'form': form})


def login_member(request):
    # Check if the user/IP is already locked out before processing the form
    if AxesProxyHandler.is_locked(request):
        messages.error(request, 'Account locked: too many login attempts. Please try again later.')
        return redirect('green_eagles:login')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('green_eagles:dashboard')
        else:
            # Check if this failed attempt just triggered a lockout
            if AxesProxyHandler.is_locked(request):
                messages.error(request, 'Account locked: too many login attempts. Please try again later.')
                return redirect('green_eagles:login')
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
            profile, _ = MemberProfile.objects.get_or_create(user=user)
            profile.wing = wing
            profile.phone = phone
            profile.save()
            
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
@wing_required('GE')
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
@wing_required('MOP')
def mop_dashboard(request):
    """Dedicated dashboard for Messengers of Peace members and admins."""
    profile, _ = MemberProfile.objects.get_or_create(user=request.user)
    announcements = Announcement.objects.filter(target_wing__in=['ALL', 'MOP'])[:5]
    
    context = {
        'profile': profile,
        'announcements': announcements,
    }
    return render(request, 'green_eagles/mop/dashboard.html', context)

def locked_out(request):
    return render(request, 'green_eagles/locked.html')

@login_required
def activity_reports(request):
    profile, _ = MemberProfile.objects.get_or_create(user=request.user)
    return render(request, 'green_eagles/activity_reports.html', {'profile': profile})

@login_required
def patrol_roster(request):
    profile, _ = MemberProfile.objects.get_or_create(user=request.user)
    # Fetch members depending on their wing or show all if EXEC/Superuser
    if request.user.is_superuser or profile.role == 'EXEC' or profile.wing == 'BOTH':
        members = MemberProfile.objects.select_related('user').all()
    else:
        members = MemberProfile.objects.select_related('user').filter(wing=profile.wing)
        
    context = {
        'profile': profile,
        'members': members,
    }
    return render(request, 'green_eagles/patrol_roster.html', context)

@login_required
def payment_waiting(request):
    profile, _ = MemberProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Allow user to retry STK push if they missed it
        phone_number = request.POST.get('phone_number') or request.POST.get('phone') or profile.phone or ''
        phone_number = ''.join(character for character in phone_number.strip() if character.isdigit())
        if phone_number.startswith('0'):
            phone_number = '254' + phone_number[1:]
        elif len(phone_number) == 9 and phone_number[0] in ('1', '7'):
            phone_number = '254' + phone_number
        amount = 500 if profile.scarf_balance > 0 else 300
        
        if not phone_number:
            messages.error(request, 'Enter a valid M-Pesa phone number to resend the payment prompt.')
        else:
            try:
                # Dynamic account reference based on amount and profile wing
                if amount == 300:
                    account_reference = "Green Eagles" if profile.wing == 'GE' else "Messengers"
                else:
                    account_reference = "Plastout Acct"

                cl = MpesaClient()
                stk_response = cl.stk_push(
                    phone_number,
                    amount,
                    account_reference[:12],
                    "PLASTOUT Fee",
                    settings.MPESA_CALLBACK_URL,
                )
                if stk_response.response_code == '0':
                    messages.success(request, 'STK Push sent to your phone! Please enter your M-Pesa PIN to complete registration.')
                else:
                    messages.error(
                        request,
                        stk_response.error_message or stk_response.response_description or 'Daraja STK push failed.',
                    )
            except Exception as e:
                messages.error(request, f'Payment gateway error: {e}')
            
        return redirect('green_eagles:payment_waiting')

    return render(request, 'green_eagles/payment_waiting.html', {'profile': profile})
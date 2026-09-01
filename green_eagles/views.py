from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ContactForm
from django.core.mail import send_mail
from django.conf import settings

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

        full_message = f"You received a new message from the PLASTOUT contact form:\n\n" \
                       f"Name: {name}\n" \
                       f"Email: {email}\n" \
                       f"Subject: {subject}\n\n" \
                       f"Message:\n{message}"

        recipient_list = ['plastout.org@gmail.com']

        try:
            send_mail(
                subject=f"PLASTOUT Contact: {subject}",
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

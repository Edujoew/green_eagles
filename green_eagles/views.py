from django.shortcuts import render
from django.shortcuts import render

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

from django.urls import path
from . import views

app_name = 'green_eagles'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),       
    path('contact/', views.contact, name='contact'), 
    path('services/', views.services, name='services'),
    path('faq/', views.faq, name='faq'),
    path('wings/green-eagles-crew/', views.green_eagles_crew, name='green_eagles_crew'),
    path('wings/messengers-of-peace/', views.messengers_of_peace, name='messengers_of_peace'), 
    path('gallery/', views.gallery, name='gallery'),
    path('register/', views.register_member, name='register'),
    path('login/', views.login_member, name='login'),
    path('logout/', views.logout_member, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),            
]
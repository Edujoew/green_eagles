from django.urls import path
from . import views

app_name = 'green_eagles'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),      
    path('contact/', views.contact, name='contact'), 
    path('services/', views.services, name='services'),
    path('faq/', views.faq, name='faq'),
    
    # --- Green Eagles Crew Wing Routes ---
    path('wings/green-eagles-crew/', views.green_eagles_crew, name='green_eagles_crew'),
    path('wings/green-eagles-crew/about/', views.crew_about, name='crew_about'),
    path('wings/green-eagles-crew/activities/', views.crew_activities, name='crew_activities'),
    path('wings/green-eagles-crew/gallery/', views.crew_gallery, name='crew_gallery'),
    path('wings/green-eagles-crew/faq/', views.crew_faq, name='crew_faq'),

    # --- Messengers of Peace (MOP) Wing Routes ---
    path('wings/messengers-of-peace/', views.messengers_of_peace, name='messengers_of_peace'), 
    path('wings/messengers-of-peace/about/', views.mop_about, name='mop_about'),
    path('wings/messengers-of-peace/activities/', views.mop_activities, name='mop_activities'),
    path('wings/messengers-of-peace/gallery/', views.mop_gallery, name='mop_gallery'),
    path('wings/messengers-of-peace/faq/', views.mop_faq, name='mop_faq'),

    # --- Member & Admin Routes ---
    path('register/', views.register_member, name='register'),
    path('login/', views.login_member, name='login'),
    path('logout/', views.logout_member, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/edit/', views.edit_profile, name='edit_profile'),
    path('gallery/', views.gallery, name='gallery'),
    path('gallery/add/', views.gallery_create, name='gallery_create'),
    path('gallery/edit/<int:pk>/', views.gallery_update, name='gallery_update'),
    path('gallery/delete/<int:pk>/', views.gallery_delete, name='gallery_delete'),
    path('admin-panel/members/', views.manage_members, name='admin_manage_members'),
    path('admin-panel/members/add/', views.admin_add_member, name='admin_add_member'),
    path('admin-panel/members/<int:pk>/edit/', views.admin_edit_member, name='admin_edit_member'),
    path('admin-panel/members/<int:pk>/delete/', views.admin_delete_member, name='admin_delete_member'),
    path('announcements/new/', views.post_announcement, name='post_announcement'),
    path('announcements/<int:pk>/delete/', views.delete_announcement, name='delete_announcement'),
    path('crew/dashboard/', views.crew_dashboard, name='crew_dashboard'),
    path('mop/dashboard/', views.mop_dashboard, name='mop_dashboard'),
]
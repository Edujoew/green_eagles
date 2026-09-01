from django.contrib import admin
from .models import Organization, Crew, Patrol, ScoutProfile
from .models import ContactMessage

# Register your models here.
@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'website')

@admin.register(Crew)
class CrewAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization', 'established_date')

@admin.register(Patrol)
class PatrolAdmin(admin.ModelAdmin):
    list_display = ('name', 'crew')

@admin.register(ScoutProfile)
class ScoutProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'crew', 'patrol')
    list_filter = ('role', 'crew')

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('created_at',)
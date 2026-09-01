from django.contrib import admin
from .models import Organization, Crew, Patrol, ScoutProfile
from .models import ContactMessage
from .models import MemberProfile

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

@admin.register(MemberProfile)
class MemberProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'wing', 'role', 'phone', 'patrol_name')
    list_filter = ('wing', 'role')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email', 'patrol_name')
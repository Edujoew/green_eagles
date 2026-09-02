from django.db import models
from django.contrib.auth.models import User

# Create your models here.
# (PLASTOUT)
class Organization(models.Model):
    name = models.CharField(max_length=100, default="PLASTOUT")
    description = models.TextField()
    website = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name

    # Green Eagles Crew model
class Crew(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='crews')
    name = models.CharField(max_length=100, default="Green Eagles Crew")
    motto = models.CharField(max_length=255, blank=True)
    established_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.organization.name})"

    # Patrols inside the Crew
class Patrol(models.Model):
    crew = models.ForeignKey(Crew, on_delete=models.CASCADE, related_name='patrols')
    name = models.CharField(max_length=50) # e.g. Cobra Patrol, Hawk Patrol

    def __str__(self):
        return self.name

class ScoutProfile(models.Model):
    ROLE_CHOICES = [
        ('SCOUT', 'Scout'),
        ('PATROL_LEADER', 'Patrol Leader'),
        ('CREW_LEADER', 'Crew Leader'),
        ('SUPERUSER', 'Superuser / Admin'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    crew = models.ForeignKey(Crew, on_delete=models.SET_NULL, null=True, blank=True)
    patrol = models.ForeignKey(Patrol, on_delete=models.SET_NULL, null=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='SCOUT')
    rank = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.subject}"    

class MemberProfile(models.Model):
    WING_CHOICES = [
        ('GE', 'Green Eagles Crew'),
        ('MOP', 'Messengers of Peace'),
        ('BOTH', 'Both Wings'),
    ]

    ROLE_CHOICES = [
        ('MEMBER', 'Volunteer / Scout Member'),
        ('PATROL_LEADER', 'Patrol Leader'),
        ('COORDINATOR', 'Wing Coordinator'),
        ('EXEC', 'Executive Admin'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=15, blank=True)
    wing = models.CharField(max_length=10, choices=WING_CHOICES, default='GE')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='MEMBER')
    patrol_name = models.CharField(max_length=50, blank=True, help_text="e.g. Rhino Patrol, Eagle Patrol")

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.get_wing_display()}"
    
class GalleryItem(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='gallery_photos/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
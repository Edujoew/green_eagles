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
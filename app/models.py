from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.CharField(max_length=255, blank=True)
    picture = models.ImageField(upload_to='profile_pictures/', blank=True, default='profile_pictures/profile.jpg')

    def __str__(self):
        return self.user.username

class Login(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    successful = models.BooleanField()

    def __str__(self):
        return f"{self.user.username} - {'Successful' if self.successful else 'Failed'} at {self.timestamp}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class Recipe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipes', default=1)  # Provide a default user ID
    title = models.CharField(max_length=255)
    ingredients = models.TextField()
    instructions = models.TextField()
    cooking_time = models.IntegerField()
    preparation_time = models.IntegerField()
    serving_size = models.IntegerField()
    tips = models.TextField(blank=True, null=True)
    picture = models.ImageField(upload_to='recipes/', blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title
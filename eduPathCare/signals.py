# your_app/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User

@receiver(post_save, sender=User)
def create_mentor_profile(sender, instance, created, **kwargs):
    """
    Signal to create a Mentor profile when a user with the role of 'mentor' is created.
    """
    # if created and instance.role == 'mentor':
    #     Mentor.objects.create(user=instance)
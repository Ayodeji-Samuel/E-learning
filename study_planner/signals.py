from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Course, CourseProgress, UserPreferences, StudySession  # Import StudySession

@receiver(post_save, sender=Course)
def create_course_progress(sender, instance, created, **kwargs):
    """
    Automatically creates a CourseProgress instance when a Course is created.
    """
    if created:
        CourseProgress.objects.create(course=instance)

@receiver(post_save, sender=StudySession)  # Now StudySession is defined
def update_course_progress(sender, instance, created, **kwargs):
    """
    Updates CourseProgress when a StudySession is completed.
    """
    if instance.is_completed:
        progress = instance.course.progress
        progress.hours_studied += instance.duration
        progress.last_studied = instance.end_time
        progress.save()

@receiver(post_save, sender=User)
def create_user_preferences(sender, instance, created, **kwargs):
    """
    Automatically creates a UserPreferences instance when a User is created.
    """
    if created:
        UserPreferences.objects.create(user=instance)
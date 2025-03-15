from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings

class Course(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='courses')
    name = models.CharField(max_length=200)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='medium')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    total_study_hours = models.FloatField(validators=[MinValueValidator(0.5)], default=10)  # Total hours needed
    deadline = models.DateField(null=True, blank=True)  # Optional deadline
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.user.username})"

class Commitment(models.Model):
    RECURRENCE_CHOICES = [
        ('none', 'None'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='commitments')
    title = models.CharField(max_length=200)
    start_time = models.DateTimeField()  # Start of busy period
    end_time = models.DateTimeField()  # End of busy period
    is_recurring = models.BooleanField(default=False)
    recurrence = models.CharField(max_length=10, choices=RECURRENCE_CHOICES, default='none')
    notes = models.TextField(blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'start_time']),  # Optimize time-based queries
        ]

    def __str__(self):
        return f"{self.title} - {self.user.username}"

class StudySession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='study_sessions')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='sessions')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_completed = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    @property
    def duration(self):
        return (self.end_time - self.start_time).total_seconds() / 3600  # Duration in hours

    class Meta:
        ordering = ['start_time']

    def __str__(self):
        return f"{self.course.name} - {self.start_time.strftime('%Y-%m-%d %H:%M')}"

class CourseProgress(models.Model):
    course = models.OneToOneField(Course, on_delete=models.CASCADE, related_name='progress')
    hours_studied = models.FloatField(default=0)
    last_studied = models.DateTimeField(null=True, blank=True)

    @property
    def remaining_hours(self):
        return max(self.course.total_study_hours - self.hours_studied, 0)

    def __str__(self):
        return f"Progress for {self.course.name}"

class Achievement(models.Model):
    ACHIEVEMENT_TYPES = [
        ('streak', 'Study Streak'),
        ('course_complete', 'Course Completed'),
        ('milestone', 'Study Milestone'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField()
    type = models.CharField(max_length=20, choices=ACHIEVEMENT_TYPES)
    threshold = models.IntegerField()  # e.g., 7-day streak, 50 hours studied

    def __str__(self):
        return self.name

class UserAchievement(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    date_earned = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'achievement')

    def __str__(self):
        return f"{self.user.username} - {self.achievement.name}"

class UserPreferences(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='preferences')
    daily_study_limit = models.FloatField(
        default=4,
        validators=[MinValueValidator(1), MaxValueValidator(12)]
    )
    preferred_study_times = models.JSONField(default=dict)  # e.g., {"mornings": True, "evenings": False}
    break_interval = models.IntegerField(default=25)  # Minutes (Pomodoro-style)
    break_duration = models.IntegerField(default=5)   # Minutes

    def __str__(self):
        return f"Preferences for {self.user.username}"
#eduPathCare/models.py

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from datetime import timedelta
from django.conf import settings

# Custom User Manager
class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        extra_fields.setdefault('is_staff', False)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None):
        user = self.create_user(username, email, password, role='mentor')
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('mentor', 'Mentor'),
        ('admin', 'Admin'),
    ]
    
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    coins = models.PositiveIntegerField(default=0)  # Add this line to track coins
    otp = models.CharField(max_length=6, blank=True, null=True)  # Add OTP field
    is_verified = models.BooleanField(default=False)  # Add verification status field
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return self.username
    
    def get_full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        else:
            return self.username

# Subjects Model
class Subject(models.Model):
    subject_id = models.AutoField(primary_key=True)
    subject_name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.PositiveIntegerField(default=0)  # Change to coins (integer)
    featured = models.BooleanField(default=False)
    
    def __str__(self):
        return self.subject_name

class UserSubject(models.Model):
    user_subject_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    subject = models.ForeignKey('Subject', on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    subscription_expiry = models.DateTimeField()
    is_selected = models.BooleanField(default=True)
    is_completed = models.BooleanField(default=False)
    is_paid = models.BooleanField(default=False)  # New field to track if this is a paid subscription
    trial_period_days = models.PositiveIntegerField(
        default=7,  # Default 7-day trial
        help_text="Number of days for free trial (0 for no trial)"
    )
    last_notification_sent = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When was the last trial expiration notification sent"
    )

    class Meta:
        unique_together = ('user', 'subject')
        verbose_name = "User Subject"
        verbose_name_plural = "User Subjects"

    def __str__(self):
        return f"{self.user.username} - {self.subject.subject_name}"

    def save(self, *args, **kwargs):
        # Set subscription expiry if this is a new record or trial period is being set
        if not self.pk or 'trial_period_days' in kwargs.get('update_fields', []):
            self.set_subscription_expiry()
        super().save(*args, **kwargs)

    def set_subscription_expiry(self):
        """Set the subscription expiry based on trial period"""
        if self.trial_period_days > 0 and not self.is_paid:
            self.subscription_expiry = timezone.now() + timedelta(days=self.trial_period_days)
        elif self.is_paid:
            # For paid subscriptions, you might want to set a longer period
            self.subscription_expiry = timezone.now() + timedelta(days=365)  # 1 year
        else:
            # No trial, immediate expiry
            self.subscription_expiry = timezone.now()

    def is_subscription_active(self):
        """Check if subscription is currently active"""
        return timezone.now() < self.subscription_expiry

    def days_remaining(self):
        """Calculate days remaining in trial/subscription"""
        delta = self.subscription_expiry - timezone.now()
        return delta.days if delta.days > 0 else 0

    def is_trial(self):
        """Check if this is a trial subscription"""
        return not self.is_paid and self.trial_period_days > 0

    def update_selection_status(self):
        """Update selection status based on subscription expiry"""
        if not self.is_subscription_active():
            self.is_selected = False
            self.save()

    def send_trial_expiration_notification(self):
        """Send notification about trial expiration"""
        if self.is_trial() and self.days_remaining() <= 3:
            # Check if we already sent a notification recently
            if (self.last_notification_sent is None or 
                (timezone.now() - self.last_notification_sent).days >= 1):
                
                # Send notification (implement your notification system here)
                from django.core.mail import send_mail
                subject = f"Your trial for {self.subject.subject_name} is ending soon"
                message = (
                    f"Your free trial for {self.subject.subject_name} will expire in {self.days_remaining()} days. "
                    "Subscribe now to continue learning without interruption."
                )
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [self.user.email],
                    fail_silently=True,
                )
                
                # Update notification timestamp
                self.last_notification_sent = timezone.now()
                self.save(update_fields=['last_notification_sent'])
    
    def renew_trial(self):
        """Renew an expired trial"""
        if not self.is_paid and self.trial_period_days > 0:
            self.enrolled_at = timezone.now()
            self.subscription_expiry = timezone.now() + timedelta(days=self.trial_period_days)
            self.is_selected = True
            self.save()
            return True
        return False

    @classmethod
    def create_trial_subscription(cls, user, subject):
        """Helper method to create a trial subscription"""
        return cls.objects.create(
            user=user,
            subject=subject,
            is_paid=False,
            trial_period_days=7,  # Default 7-day trial
        )

    @classmethod
    def create_paid_subscription(cls, user, subject, duration_days=365):
        """Helper method to create a paid subscription"""
        return cls.objects.create(
            user=user,
            subject=subject,
            is_paid=True,
            trial_period_days=0,  # No trial for paid subscriptions
            subscription_expiry=timezone.now() + timedelta(days=duration_days),
        )
        
    





# Sections Model
class Section(models.Model):
    section_id = models.AutoField(primary_key=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    section_name = models.CharField(max_length=255)
    section_order = models.PositiveIntegerField()
    text_content = models.TextField()
    image_content = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_completed = models.BooleanField(default=False)
    
    def __str__(self):
        return self.section_name
    

# Subsection Model
class Subsection(models.Model):
    subsection_id = models.AutoField(primary_key=True)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="subsections")
    subsection_name = models.CharField(max_length=255)
    subsection_order = models.PositiveIntegerField()
    text_content = models.TextField()
    image_content = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.section.section_name} - {self.subsection_name}"

    
   

# Questions Model
class Question(models.Model):
    OPTION_CHOICES = [
        ('a', 'A'),
        ('b', 'B'),
        ('c', 'C'),
        ('d', 'D'),
    ]
    question_id = models.AutoField(primary_key=True)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    question_text = models.TextField()
    option_a = models.TextField()
    option_b = models.TextField()
    option_c = models.TextField()
    option_d = models.TextField()
    correct_option = models.CharField(max_length=1, choices=OPTION_CHOICES)
    explanation_a = models.TextField()
    explanation_b = models.TextField()
    explanation_c = models.TextField()
    explanation_d = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def get_explanation(self, user_answer):
        if user_answer == 'a':
            return self.explanation_a
        elif user_answer == 'b':
            return self.explanation_b
        elif user_answer == 'c':
            return self.explanation_c
        elif user_answer == 'd':
            return self.explanation_d
        return "No explanation available."
    
# Quizzes Model
class Quiz(models.Model):
    quiz_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)  # Add this line
    total_score = models.PositiveIntegerField()
    attempts_count = models.PositiveIntegerField(default=1)
    completed_at = models.DateTimeField()
    time_spent = models.PositiveIntegerField(default=0)  # Time spent in seconds

    class Meta:
        unique_together = ('user', 'subject', 'section')  # Ensure only one quiz per user, subject, and section

    def __str__(self):
        return f"{self.user.username} - {self.subject.subject_name} - {self.section.section_name}"
    
    def calculate_points(self):
        questions = Question.objects.filter(section=self.section)
        total_questions = questions.count()
        if total_questions == 0:
            return 0
        percentage_score = (self.total_score / total_questions) * 100

        if percentage_score >= 90:
            return 5
        elif percentage_score >= 80:
            return 4
        elif percentage_score >= 70:
            return 3
        elif percentage_score >= 60:
            return 2
        elif percentage_score >= 50:
            return 1
        else:
            return 0


# Add to eduPathCare/models.py
class Flashcard(models.Model):
    flashcard_id = models.AutoField(primary_key=True)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='flashcards')
    question = models.TextField()
    answer = models.TextField()
    is_mastered = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Flashcard {self.order} for {self.section.section_name}"


class FinalExam(models.Model):
    final_exam_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    total_score = models.PositiveIntegerField()
    attempts_count = models.PositiveIntegerField(default=1)
    completed_at = models.DateTimeField()
    time_spent = models.PositiveIntegerField(default=0)  # Time spent in seconds

    def __str__(self):
        return f"{self.user.username} - {self.subject.subject_name} Final Exam"

    def calculate_points(self):
        questions = Question.objects.filter(section__subject=self.subject)
        total_questions = questions.count()
        if total_questions == 0:
            return 0
        percentage_score = (self.total_score / total_questions) * 100

        if percentage_score >= 90:
            return 5
        elif percentage_score >= 80:
            return 4
        elif percentage_score >= 70:
            return 3
        elif percentage_score >= 60:
            return 2
        elif percentage_score >= 50:
            return 1
        else:
            return 0
        

# User Progress Model
class UserProgress(models.Model):
    progress_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    completed_sections = models.JSONField()
    total_score = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

# eduPathCare/models.py

class UserActivity(models.Model):
    ACTIVITY_CHOICES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('subject_selected', 'Subject Selected'),
        ('quiz_attempted', 'Quiz Attempted'),
        ('final_exam_attempted', 'Final Exam Attempted'),
        ('flashcard_viewed', 'Flashcard Viewed'),
        ('coin_purchased', 'Coin Purchased'),
        ('coin_withdrawn', 'Coin Withdrawn'),
        ('profile_updated', 'Profile Updated'),
        ('password_reset', 'Password Reset'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.JSONField(blank=True, null=True)  # Store additional details about the activity

    def __str__(self):
        return f"{self.user.username} - {self.get_activity_type_display()} at {self.timestamp}"

    class Meta:
        verbose_name_plural = "User Activities"
        ordering = ['-timestamp']
        
        
        
        
# Add to models.py (after UserActivity model)
class Payment(models.Model):
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    coins_purchased = models.PositiveIntegerField()
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    receipt = models.ImageField(upload_to='payment_receipts/')
    sender_name = models.CharField(max_length=255)
    receipt_no = models.CharField(max_length=100)
    transaction_date = models.DateTimeField(auto_now_add=True)
    admin_notes = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=PAYMENT_STATUS, default='pending')
    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_payments')
    processed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.coins_purchased} coins ({self.status})"

    class Meta:
        ordering = ['-transaction_date']
        
        
        
class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.question

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'
        

class CoinPackage(models.Model):
    name = models.CharField(max_length=100)
    coins = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_popular = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['price']
        verbose_name = 'Coin Package'
        verbose_name_plural = 'Coin Packages'

    def __str__(self):
        return f"{self.coins} Coins - ₦{self.price}"
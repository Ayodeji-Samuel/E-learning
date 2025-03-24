#eduPathCare/models.py

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from datetime import timedelta

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


# UserSubject Model to track subjects selected by users
class UserSubject(models.Model):
    user_subject_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    subscription_expiry = models.DateTimeField()  # Subscription expiry date
    is_selected = models.BooleanField(default=True)  # New field to track selection
    is_completed = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Set subscription expiry to 30 days from enrollment (or any other duration)
        if not self.subscription_expiry:
            self.subscription_expiry = timezone.now() + timedelta(days=30)
        super().save(*args, **kwargs)

    def is_subscription_active(self):
        # Check if the subscription is still active
        return timezone.now() < self.subscription_expiry
    
    def update_selection_status(self):
        if self.subscription_expiry and timezone.now() > self.subscription_expiry:
            self.is_selected = False
            self.save()

    class Meta:
        unique_together = ('user', 'subject')  # Ensure a user can only select a subject once

    def __str__(self):
        return f"{self.user.username} - {self.subject.subject_name}"


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
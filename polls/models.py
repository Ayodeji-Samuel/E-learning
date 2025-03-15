from django.db import models
#from django.contrib.auth.models import User
import uuid
from django.utils import timezone
from django.conf import settings

class Poll(models.Model):
    QUESTION_TYPE_CHOICES = [
        ('MC', 'Multiple Choice'),
        ('OT', 'Open Text'),
    ]

    # Unique identifier for sharing links
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    question = models.CharField(max_length=255, unique=True)
    question_type = models.CharField(max_length=2, choices=QUESTION_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    # Toggle to activate/deactivate responses for the entire poll
    is_active = models.BooleanField(default=True)

    # Expiration time for the poll
    expiration_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.question} ({self.get_question_type_display()})"

    def is_expired(self):
        """Check if the poll has expired."""
        if self.expiration_time:
            return timezone.now() > self.expiration_time
        return False

    def can_accept_responses(self):
        """Check if the poll is active and not expired."""
        return self.is_active and not self.is_expired()

class Option(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=255)
    
    # For multiple choice votes
    votes = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.text} - {self.votes} votes"

class Participant(models.Model):
    # Unique identifier for anonymous participant tracking
    identifier = models.UUIDField(default=uuid.uuid4, editable=False)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    has_responded = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('identifier', 'poll')  # Prevent duplicate responses

    def __str__(self):
        return f"Participant {self.identifier} for {self.poll}"

class TextResponse(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    # Toggle to activate/deactivate this specific response
    is_active = models.BooleanField(default=True)

    # Expiration time for this specific response
    expiration_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Response to {self.poll} by {self.participant}"

    def is_expired(self):
        """Check if the response has expired."""
        if self.expiration_time:
            return timezone.now() > self.expiration_time
        return False

    def is_visible(self):
        """Check if the response is active and not expired."""
        return self.is_active and not self.is_expired()
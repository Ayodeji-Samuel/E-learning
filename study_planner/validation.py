from django.core.exceptions import ValidationError

def validate_study_session(session):
    """
    Validates a StudySession to ensure end_time > start_time.
    """
    if session.end_time <= session.start_time:
        raise ValidationError("End time must be after start time.")

def validate_commitment(commitment):
    """
    Validates a Commitment to ensure end_time > start_time.
    """
    if commitment.end_time <= commitment.start_time:
        raise ValidationError("End time must be after start time.")
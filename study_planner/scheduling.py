from datetime import datetime, timedelta
from .models import Course, Commitment, StudySession, UserPreferences
from django.core.exceptions import ObjectDoesNotExist

def generate_study_schedule(user):
    """
    Generates a study schedule for a user based on their courses, commitments, and preferences.
    """
    # Fetch user data
    try:
        preferences = UserPreferences.objects.get(user=user)
    except ObjectDoesNotExist:
        preferences = UserPreferences.objects.create(user=user)
    courses = Course.objects.filter(user=user)
    commitments = Commitment.objects.filter(user=user)
    #preferences = UserPreferences.objects.get(user=user)
    #preferences, created = UserPreferences.objects.get_or_create(user=user)

    # Define study parameters
    daily_limit = preferences.daily_study_limit
    break_interval = timedelta(minutes=preferences.break_interval)
    break_duration = timedelta(minutes=preferences.break_duration)
    preferred_start_time = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)  # Default start time
    preferred_end_time = datetime.now().replace(hour=21, minute=0, second=0, microsecond=0)  # Default end time

    # Initialize schedule
    schedule = []
    current_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    # Loop through each day for the next 7 days
    for _ in range(7):
        current_date += timedelta(days=1)
        day_start = current_date.replace(hour=preferred_start_time.hour, minute=preferred_start_time.minute)
        day_end = current_date.replace(hour=preferred_end_time.hour, minute=preferred_end_time.minute)

        # Filter commitments for the day
        day_commitments = [
            c for c in commitments
            if c.start_time.date() == current_date.date()
        ]

        # Sort courses by priority and difficulty
        sorted_courses = sorted(courses, key=lambda x: (x.priority, x.difficulty), reverse=True)

        # Track daily study hours
        daily_study_hours = 0

        # Allocate study sessions
        for course in sorted_courses:
            remaining_hours = course.progress.remaining_hours
            if remaining_hours <= 0:
                continue

            # Calculate session duration based on difficulty
            if course.difficulty == 'easy':
                session_duration = timedelta(hours=1)
            elif course.difficulty == 'medium':
                session_duration = timedelta(hours=1.5)
            else:  # Hard
                session_duration = timedelta(hours=2)

            # Ensure session duration doesn't exceed remaining hours
            session_duration = min(session_duration, timedelta(hours=remaining_hours))

            # Find a time slot
            session_start = day_start
            while session_start < day_end:
                # Check if the slot is available
                is_available = True
                for commitment in day_commitments:
                    if not (session_start + session_duration <= commitment.start_time or
                           session_start >= commitment.end_time):
                        is_available = False
                        break

                # Ensure daily study limit is not exceeded
                if daily_study_hours + session_duration.total_seconds() / 3600 > daily_limit:
                    break

                if is_available:
                    # Add session to schedule
                    session_end = session_start + session_duration
                    schedule.append({
                        'course': course,
                        'start_time': session_start,
                        'end_time': session_end,
                    })
                    daily_study_hours += session_duration.total_seconds() / 3600
                    session_start = session_end + break_duration
                    break

                session_start += break_interval

    return schedule
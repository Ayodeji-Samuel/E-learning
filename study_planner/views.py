from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Course, Commitment, StudySession, CourseProgress, UserPreferences, UserAchievement, Achievement
from .scheduling import generate_study_schedule
from rest_framework import viewsets, permissions
from .serializers import CourseSerializer, CommitmentSerializer, StudySessionSerializer, CourseProgressSerializer, UserAchievementSerializer, UserPreferencesSerializer, AchievementSerializer
from .forms import CourseForm, StudySessionForm  # You'll need to create these forms
from django.contrib import messages




@login_required
def dashboard(request):
    """
    Displays the user's study schedule and progress.
    """
    user = request.user
    try:
        preferences = UserPreferences.objects.get(user=user)
    except UserPreferences.DoesNotExist:
        preferences = UserPreferences.objects.create(user=user)
        
    schedule = generate_study_schedule(user)
    courses = Course.objects.filter(user=user)
    commitments = Commitment.objects.filter(user=user)
    progress = CourseProgress.objects.filter(course__user=user)

    for prog in progress:
        prog.progress_percentage = (prog.hours_studied / prog.course.total_study_hours) * 100
        
    context = {
        'schedule': schedule,
        'courses': courses,
        'commitments': commitments,
        'progress': progress,
    }
    return render(request, 'dashboard.html', context)

@login_required
def add_course(request):
    """
    View for adding a new course.
    """
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.user = request.user
            course.save()
            return redirect('study_planner:dashboard')  # Redirect to the dashboard after adding the course
    else:
        form = CourseForm()
    return render(request, 'add_course.html', {'form': form})

@login_required
def schedule_study_session(request):
    """
    View for scheduling a new study session.
    """
    if request.method == 'POST':
        form = StudySessionForm(request.POST)
        if form.is_valid():
            study_session = form.save(commit=False)
            study_session.user = request.user
            study_session.save()
            return redirect('study_planner:dashboard')  # Redirect to the dashboard after scheduling the session
    else:
        form = StudySessionForm()
    return render(request, 'schedule_study_session.html', {'form': form})


@login_required
def view_achievements(request):
    """
    View for displaying user achievements.
    """
    user = request.user
    achievements = UserAchievement.objects.filter(user=user)
    return render(request, 'view_achievements.html', {'achievements': achievements})


@login_required
def generate_schedule(request):
    """
    View for generating a new study schedule.
    """
    user = request.user
    # Delete existing study sessions for the user
    StudySession.objects.filter(user=user).delete()
    
    # Generate a new schedule
    schedule = generate_study_schedule(user)
    
    # Save the generated sessions to the database
    for session in schedule:
        StudySession.objects.create(
            user=user,
            course=session['course'],
            start_time=session['start_time'],
            end_time=session['end_time'],
        )
    messages.success(request, 'Your study schedule has been generated successfully!')
    return redirect('study_planner:dashboard')  # Redirect to the dashboard after generating the schedule



class CourseViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing courses.
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only return courses for the logged-in user
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Automatically assign the logged-in user as the course owner
        serializer.save(user=self.request.user)

class CommitmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing commitments.
    """
    queryset = Commitment.objects.all()
    serializer_class = CommitmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only return commitments for the logged-in user
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Automatically assign the logged-in user as the commitment owner
        serializer.save(user=self.request.user)

class StudySessionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing study sessions.
    """
    queryset = StudySession.objects.all()
    serializer_class = StudySessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only return study sessions for the logged-in user
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Automatically assign the logged-in user as the study session owner
        serializer.save(user=self.request.user)
        

class CourseProgressViewSet(viewsets.ModelViewSet):
    queryset = CourseProgress.objects.all()
    serializer_class = CourseProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only return progress for the logged-in user's courses
        return self.queryset.filter(course__user=self.request.user)
    

class AchievementViewSet(viewsets.ModelViewSet):
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializer
    permission_classes = [permissions.IsAuthenticated]
    

class UserAchievementViewSet(viewsets.ModelViewSet):
    queryset = UserAchievement.objects.all()
    serializer_class = UserAchievementSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only return achievements for the logged-in user
        return self.queryset.filter(user=self.request.user)
    

class UserPreferencesViewSet(viewsets.ModelViewSet):
    queryset = UserPreferences.objects.all()
    serializer_class = UserPreferencesSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only return preferences for the logged-in user
        return self.queryset.filter(user=self.request.user)
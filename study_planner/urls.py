from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (dashboard, CourseViewSet, CommitmentViewSet, StudySessionViewSet, add_course, schedule_study_session, 
view_achievements, CourseProgressViewSet, AchievementViewSet, UserAchievementViewSet, UserPreferencesViewSet, generate_schedule)


router = DefaultRouter()
router.register(r'courses', CourseViewSet)
router.register(r'commitments', CommitmentViewSet)
router.register(r'study-sessions', StudySessionViewSet)
router.register(r'course-progress', CourseProgressViewSet)
router.register(r'achievements', AchievementViewSet)
router.register(r'user-achievements', UserAchievementViewSet)
router.register(r'user-preferences', UserPreferencesViewSet)

app_name = 'study_planner'

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('api/', include(router.urls)),
    path('add-course/', add_course, name='add_course'),  # URL for adding a new course
    path('schedule-study-session/', schedule_study_session, name='schedule_study_session'),  # URL for scheduling a study session
    path('view-achievements/', view_achievements, name='view_achievements'),
    path('generate-schedule/', generate_schedule, name='generate_schedule'),  # New URL for generating the schedule
]
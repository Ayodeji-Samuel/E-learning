from django.contrib import admin

# Register your models here.
from .models import Course, CourseProgress, StudySession, UserPreferences


admin.site.register(Course)
admin.site.register(CourseProgress)
admin.site.register(StudySession)
admin.site.register(UserPreferences)

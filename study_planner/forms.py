from django import forms
from .models import Course, StudySession

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name', 'difficulty', 'priority', 'total_study_hours', 'deadline']

class StudySessionForm(forms.ModelForm):
    class Meta:
        model = StudySession
        fields = ['course', 'start_time', 'end_time', 'notes']
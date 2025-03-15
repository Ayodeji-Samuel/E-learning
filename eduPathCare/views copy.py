from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import User, Subject, Section
from .forms import SignUpForm, PasswordResetForm, SubjectForm, SectionForm
from django.utils import timezone
from django.db.models import F
import uuid


def index(request):
   featured_subjects = Subject.objects.filter(featured=True)[:4]
   
   stats = {
       'learners': User.objects.filter(role='student').count(),
       'mentors': User.objects.filter(role='mentor').count(),
       'sections': Section.objects.count()
   }

   context = {
       'featured_subjects': featured_subjects,
       'stats': stats
   }
   
   return render(request, 'index.html', context)

# Optional: Add featured field to Subject model if not present
"""
class Subject(models.Model):
   # ... existing fields ...
   featured = models.BooleanField(default=False)
"""

# Sign Up View
def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('subjects_list')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

# Login View
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('subjects_list')
        else:
            messages.error(request, 'Invalid username or password')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

# Forgot Password View
def forgot_password_view(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Password reset instructions sent to your email')
            return redirect('login')
    else:
        form = PasswordResetForm()
    return render(request, 'passwordReset.html', {'form': form})

# write the logout view here
def logout_view(request):
    logout(request)
    return redirect('login')


# Subjects List View
@login_required
def subjects_list_view(request):
    subjects = Subject.objects.all()
    return render(request, 'subjectsList.html', {'subjects': subjects})

# Subject Details View
@login_required
def subject_details_view(request, subject_id):
    subject = get_object_or_404(Subject, subject_id=subject_id)
    #sections = Section.objects.filter(subject=subject.subject_id)
    sections = subject.section_set.all()
    return render(request, 'subjectDetails.html', {'subject': subject, 'sections': sections})

# Section Content View
@login_required
def section_content_view(request, section_id):
    section = get_object_or_404(Section, section_id=section_id)
    subject = section.subject
    sections = Section.objects.filter(subject=subject)
    return render(request, 'sectionContent.html', {'section': section, 'sections': sections})


@login_required
def create_subject(request):
    if request.method == "POST":
        form = SubjectForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('subjects_list')  # Redirect to subjects list
    else:
        form = SubjectForm()
    return render(request, 'create_subject.html', {'form': form})

# Create Section View
@login_required
def create_section(request, subject_id):
    subject = Subject.objects.get(subject_id=subject_id)
    if request.method == "POST":
        form = SectionForm(request.POST, request.FILES)
        if form.is_valid():
            section = form.save(commit=False)
            section.subject = subject
            section.save()

            # Process dynamic text and image fields
            text_contents = [value for key, value in request.POST.items() if key.startswith('text_content_')]
            image_contents = [value for key, value in request.POST.items() if key.startswith('image_content_')]

            for text, image in zip(text_contents, image_contents):
                # Save text and image content to the section (or a related model)
                pass  # Add your logic here

            return redirect('subject_details', subject_id=subject.subject_id)
    else:
        form = SectionForm()
    return render(request, 'create_section.html', {'form': form, 'subject': subject})


# Delete Section View
@login_required
def delete_section(request, section_id):
    section = get_object_or_404(Section, section_id=section_id)
    subject_id = section.subject.subject_id  # Get the subject ID before deleting
    section.delete()
    return redirect('subject_details', subject_id=subject_id)


@login_required
def edit_section(request, section_id):
    section = get_object_or_404(Section, section_id=section_id)
    subject = section.subject

    if request.method == "POST":
        form = SectionForm(request.POST, request.FILES, instance=section)
        if form.is_valid():
            form.save()

            # Process dynamic text and image fields
            text_contents = [value for key, value in request.POST.items() if key.startswith('text_content_')]
            image_contents = [value for key, value in request.POST.items() if key.startswith('image_content_')]

            for text, image in zip(text_contents, image_contents):
                # Save text and image content to the section (or a related model)
                pass  # Add your logic here

            return redirect('subject_details', subject_id=subject.subject_id)
    else:
        form = SectionForm(instance=section)

    return render(request, 'edit_section.html', {'form': form, 'subject': subject, 'section': section})

#================================================================================================

from .models import Question, Quiz, UserProgress, Section
from .forms import QuizForm

@login_required
def quiz_view(request, section_id):
    section = get_object_or_404(Section, section_id=section_id)
    questions = Question.objects.filter(section=section)
    
    if request.method == 'POST':
        form = QuizForm(request.POST, questions=questions)
        if form.is_valid():
            score = 0
            results = []
            
            # Get or create the quiz record for the user, subject, and section
            quiz, created = Quiz.objects.get_or_create(
                user=request.user,
                subject=section.subject,
                section=section,
                defaults={
                    'total_score': 0,
                    'attempts_count': 0,
                    'completed_at': timezone.now()
                }
            )
            
            # Calculate the score for the current attempt
            for question in questions:
                user_answer = form.cleaned_data.get(f'question_{question.question_id}')
                is_correct = user_answer == question.correct_option
                if is_correct:
                    score += 1
                
                results.append({
                    'question': question.question_text,
                    'user_answer': user_answer,
                    'correct_answer': question.correct_option,
                    'is_correct': is_correct,
                    'explanation': getattr(question, f'explanation_{user_answer}') if user_answer else None,
                })
            
            # Update the quiz record with the new score and attempt count
            quiz.total_score = score
            quiz.attempts_count += 1
            quiz.completed_at = timezone.now()
            quiz.save()

            # Update user progress
            user_progress, created = UserProgress.objects.get_or_create(
                user=request.user,
                subject=section.subject,
                defaults={
                    'completed_sections': [],
                    'total_score': 0,
                }
            )
            completed_sections = user_progress.completed_sections or []
            
            # Mark the section as complete if the score is above 90%
            percentage_score = (score / len(questions)) * 100 if len(questions) > 0 else 0
            if percentage_score >= 90 and section_id not in user_progress.completed_sections:
                user_progress.completed_sections.append(section_id)
                user_progress.total_score += score
                user_progress.save()

            return render(request, 'quiz_results.html', {
                'section': section,
                'results': results,
                'score': score,
                'total_questions': len(questions),
                'percentage_score': percentage_score,
            })
    else:
        form = QuizForm(questions=questions)
    
    return render(request, 'quiz.html', {
        'section': section,
        'form': form,
        'questions': questions,
    })

  
    
from .forms import QuestionForm

@login_required
def create_quiz(request, section_id):
    # Ensure only mentors can access this page
    if request.user.role != 'mentor':
        messages.error(request, 'You do not have permission to create quizzes.')
        return redirect('subjects_list')

    section = get_object_or_404(Section, section_id=section_id)
    questions = Question.objects.filter(section=section)

    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.section = section
            question.save()
            messages.success(request, 'Question added successfully!')
            return redirect('create_quiz', section_id=section_id)
    else:
        form = QuestionForm()

    return render(request, 'create_quiz.html', {
        'section': section,
        'questions': questions,
        'form': form,
    })

@login_required
def edit_question(request, question_id):
    # Ensure only mentors can access this page
    if request.user.role != 'mentor':
        messages.error(request, 'You do not have permission to edit questions.')
        return redirect('subjects_list')

    question = get_object_or_404(Question, question_id=question_id)
    section = question.section

    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            messages.success(request, 'Question updated successfully!')
            return redirect('create_quiz', section_id=section.section_id)
    else:
        form = QuestionForm(instance=question)

    return render(request, 'edit_question.html', {
        'form': form,
        'question': question,
    })

@login_required
def delete_question(request, question_id):
    # Ensure only mentors can access this page
    if request.user.role != 'mentor':
        messages.error(request, 'You do not have permission to delete questions.')
        return redirect('subjects_list')

    question = get_object_or_404(Question, question_id=question_id)
    section_id = question.section.section_id
    question.delete()
    messages.success(request, 'Question deleted successfully!')
    return redirect('create_quiz', section_id=section_id)


#===================================================================================================

@login_required
def student_dashboard(request):
    # Ensure only students can access this page
    if request.user.role != 'student':
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('subjects_list')

    # Get the student's progress
    user_progress = UserProgress.objects.filter(user=request.user)

    # Calculate overall progress
    total_sections_completed = sum(len(progress.completed_sections) for progress in user_progress)
    total_sections = Section.objects.count()  # Total sections across all subjects
    overall_progress = (total_sections_completed / total_sections) * 100 if total_sections > 0 else 0

    # Prepare quiz performance data per subject and section
    quiz_performance = []
    for progress in user_progress:
        subject = progress.subject
        sections = Section.objects.filter(subject=subject)
        
        for section in sections:
            # Get the most recent quiz attempt for the section
            quiz = Quiz.objects.filter(
                user=request.user,
                subject=subject,
                section=section
            ).order_by('-completed_at').first()
            
            if quiz:
                # Get all questions for the section
                questions = Question.objects.filter(section=section)
                total_questions = questions.count()
                
                # Calculate percentage score based on the most recent attempt
                percentage_score = (quiz.total_score / total_questions) * 100 if total_questions > 0 else 0
                
                # Determine remark based on percentage score
                if percentage_score >= 90:
                    remark = "Excellent"
                    badge_class = "bg-success"
                elif percentage_score >= 70:
                    remark = "Good"
                    badge_class = "bg-primary"
                elif percentage_score >= 50:
                    remark = "Needs Improvement"
                    badge_class = "bg-warning"
                else:
                    remark = "Poor"
                    badge_class = "bg-danger"
                
                quiz_performance.append({
                    'subject': subject,
                    'section': section,
                    'percentage_score': percentage_score,
                    'remark': remark,
                    'badge_class': badge_class,
                })

    # Get recommended topics (e.g., sections with the lowest scores)
    recommended_sections = [performance['section'] for performance in quiz_performance if performance['percentage_score'] < 70]

    return render(request, 'student_dashboard.html', {
        'user_progress': user_progress,
        'quiz_performance': quiz_performance,
        'overall_progress': overall_progress,
        'recommended_sections': recommended_sections,
    })

@login_required
def ladderboard_view(request):
    # Get all students
    students = User.objects.filter(role='student')

    # Calculate cumulative points for each student
    student_points = []
    for student in students:
        quizzes = Quiz.objects.filter(user=student)
        total_points = sum(quiz.calculate_points() for quiz in quizzes)
        student_points.append({
            'student': student,
            'total_points': total_points
        })

    # Sort students by total points in ascending order
    student_points.sort(key=lambda x: x['total_points'])

    return render(request, 'ladderboard.html', {
        'student_points': student_points
    })


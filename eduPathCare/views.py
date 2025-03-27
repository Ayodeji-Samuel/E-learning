# eduPathCare/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from asgiref.sync import sync_to_async
from .models import User, Subject, Section, Question, Quiz, UserProgress, UserSubject, Subsection, FinalExam, UserActivity
from .forms import SignUpForm, PasswordResetForm, SubjectForm, SectionForm, QuizForm, QuestionForm, CSVUploadForm, SubsectionForm
import csv
from django.db.models import F

### 🚀 Helper functions optimized to avoid redundant async wrapping
def get_object_or_404_sync(model, *args, **kwargs):
    return get_object_or_404(model, *args, **kwargs)

def get_user_progress(user):
    return list(UserProgress.objects.filter(user=user))

def get_quiz(user, subject, section):
    return Quiz.objects.filter(user=user, subject=subject, section=section).order_by('-completed_at').first()

def get_questions(section):
    return list(Question.objects.filter(section=section))

def save_quiz(quiz):
    quiz.save()

def save_user_progress(user_progress):
    user_progress.save()

def get_students():
    return list(User.objects.filter(role='student'))

def get_quizzes(student):
    return list(Quiz.objects.filter(user=student))


#Index View
async def index(request):
    featured_subjects = await sync_to_async(list)(Subject.objects.filter(featured=True)[:4])
    stats = {
        'learners': await sync_to_async(User.objects.filter(role='student').count)(),
        'mentors': await sync_to_async(User.objects.filter(role='mentor').count)(),
        'sections': await sync_to_async(Section.objects.count)(),
    }
    context = {
        'featured_subjects': featured_subjects,
        'stats': stats
    }
    return await sync_to_async(render)(request, 'index.html', context)


def dashboard_view(request):
    """
    Renders the dashboard page with all app links.
    """
    return render(request, 'dashboard.html')


import random
from django.core.mail import send_mail
from django.conf import settings

import logging

logger = logging.getLogger(__name__)

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_verified = False
            user.save()

            otp = ''.join(random.choices('0123456789', k=6))
            user.otp = otp
            user.save()

            try:
                send_mail(
                    'Your OTP for AnSaSphere',
                    f'Your OTP is: {otp}',
                    settings.EMAIL_HOST_USER,
                    [user.email],
                    fail_silently=False,
                )
                logger.info(f"OTP sent to {user.email}")
            except Exception as e:
                logger.error(f"Failed to send OTP to {user.email}: {e}")

            return redirect('verify_otp', user_id=user.user_id)
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


#Verify OTP View

def verify_otp_view(request, user_id):
    user = User.objects.get(user_id=user_id)
    
    if request.method == 'POST':
        otp_entered = request.POST.get('otp')
        
        if otp_entered == user.otp:
            user.is_verified = True
            user.otp = None  # Clear the OTP after verification
            user.save()
            messages.success(request, 'Email verified successfully! You can now log in.')
            return redirect('login')
        else:
            messages.error(request, 'Invalid OTP. Please try again.')
    
    return render(request, 'verify_otp.html', {'user_id': user_id})




def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_verified:
                login(request, user)
                UserActivity.objects.create(user=user, activity_type='login')
                return redirect('dashboard')
            else:
                messages.error(request, 'Your email is not verified. Please check your email for the OTP.')
        else:
            messages.error(request, 'Invalid username or password')
    else:
        form = AuthenticationForm()
    
    return render(request, 'login.html', {'form': form})



def logout_view(request):
    if request.user.is_authenticated:
        # Log the logout activity
        UserActivity.objects.create(user=request.user, activity_type='logout')
    logout(request)
    return redirect('login')



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


@login_required
def subjects_list_view(request):
    subjects = Subject.objects.all()
    user_subjects = UserSubject.objects.filter(user=request.user).select_related('subject')
    
    # Create dictionaries for different subscription states
    user_subject_dict = {us.subject_id: us for us in user_subjects}
    active_subscriptions = [us for us in user_subjects if us.is_subscription_active()]
    expired_subscriptions = [us for us in user_subjects if not us.is_subscription_active()]
    
    context = {
        'subjects': subjects,
        'user_subject_dict': user_subject_dict,
        'active_subscriptions': active_subscriptions,
        'expired_subscriptions': expired_subscriptions,
        'has_active_subscriptions': len(active_subscriptions) > 0,
    }
    return render(request, 'subjectsList.html', context)



@login_required
def subject_details_view(request, subject_id):
    subject = get_object_or_404_sync(Subject, subject_id=subject_id)
    sections = subject.section_set.all()
    return render(request, 'subjectDetails.html', {'subject': subject, 'sections': sections})

@login_required
def section_content_view(request, section_id):
    section = get_object_or_404_sync(Section, section_id=section_id)
    subject = section.subject
    sections = Section.objects.filter(subject=subject)
    return render(request, 'sectionContent.html', {'section': section, 'sections': sections})

#===================================================================================================

@login_required
def quiz_view(request, section_id):
    section = get_object_or_404(Section, section_id=section_id)
    questions = Question.objects.filter(section=section)
    
    if not questions.exists():
        messages.warning(request, "This section has no questions yet.")
        return redirect('sections_list_quiz', subject_id=section.subject.subject_id)

    if request.method == 'POST':
        form = QuizForm(request.POST, questions=questions)
        if form.is_valid():
            score = 0
            results = []
            
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
                    'explanation': question.get_explanation(user_answer),
                })

            time_spent = int(request.POST.get('time_spent', 1800))
            minutes = time_spent // 60
            seconds = time_spent % 60

            subject = section.subject

            quiz, created = Quiz.objects.get_or_create(
                user=request.user,
                section=section,
                defaults={
                    'subject': subject,
                    'total_score': score,
                    'attempts_count': 1,
                    'completed_at': timezone.now(),
                    'time_spent': time_spent
                }
            )

            if not created:
                quiz.total_score = score
                quiz.attempts_count += 1
                quiz.completed_at = timezone.now()
                quiz.time_spent = time_spent
                quiz.save()

            # Log the quiz attempt activity
            UserActivity.objects.create(
                user=request.user,
                activity_type='quiz_attempted',
                details={
                    'section_id': section.section_id,
                    'section_name': section.section_name,
                    'score': score,
                    'total_questions': len(questions),
                    'percentage_score': round((score / len(questions)) * 100, 2),
                    'time_spent': time_spent,
                }
            )

            user_progress, created = UserProgress.objects.get_or_create(
                user=request.user,
                subject=subject,
                defaults={'completed_sections': [], 'total_score': 0}
            )
            
            if (score / len(questions)) * 100 >= 70:
                if section.section_id not in user_progress.completed_sections:
                    user_progress.completed_sections.append(section.section_id)
                    user_progress.total_score += score
                    user_progress.save()

            return render(request, 'quiz_results.html', {
                'section': section,
                'results': results,
                'score': score,
                'total_questions': len(questions),
                'percentage_score': round((score / len(questions)) * 100, 2),
                'time_spent_minutes': minutes,
                'time_spent_seconds': seconds,
            })

    return render(request, 'quiz.html', {
        'section': section,
        'form': QuizForm(questions=questions)
    })





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

#=====================================================================================================

# Student Dashboard View
@login_required
def student_dashboard(request):
    if request.user.role != 'student':
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('subjects_list')

    # Efficiently fetch user progress
    user_progress = UserProgress.objects.filter(user=request.user).select_related('subject')

    # Count completed sections efficiently
    total_sections_completed = sum(len(progress.completed_sections) for progress in user_progress)
    total_sections = Section.objects.count()
    overall_progress = (total_sections_completed / total_sections) * 100 if total_sections > 0 else 0

    # Fetch quizzes in bulk to reduce queries
    quizzes = Quiz.objects.filter(user=request.user).select_related('section', 'subject')
    
    quiz_performance = []
    for quiz in quizzes:
        total_questions = Question.objects.filter(section=quiz.section).count()
        percentage_score = (quiz.total_score / total_questions) * 100 if total_questions > 0 else 0
        
        if percentage_score >= 90:
            remark, badge_class = "Excellent", "bg-success"
        elif percentage_score >= 70:
            remark, badge_class = "Good", "bg-primary"
        elif percentage_score >= 50:
            remark, badge_class = "Needs Improvement", "bg-warning"
        else:
            remark, badge_class = "Poor", "bg-danger"
        
        quiz_performance.append({
            'subject': quiz.subject,
            'section': quiz.section,
            'percentage_score': percentage_score,
            'remark': remark,
            'badge_class': badge_class,
        })

    recommended_sections = [performance['section'] for performance in quiz_performance if performance['percentage_score'] < 70]

    return render(request, 'student_dashboard.html', {
        'user_progress': user_progress,
        'quiz_performance': quiz_performance,
        'overall_progress': overall_progress,
        'recommended_sections': recommended_sections,
    })

# Ladderboard View
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
    

@login_required
def upload_questions_csv(request):
    if request.user.role != 'mentor' and not request.user.is_superuser:
        messages.error(request, 'You do not have permission to upload questions.')
        return redirect('subjects_list')

    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            if not csv_file.name.endswith('.csv'):
                messages.error(request, 'Please upload a valid CSV file.')
                return redirect('upload_questions_csv')

            try:
                decoded_file = csv_file.read().decode('utf-8').splitlines()
                reader = csv.DictReader(decoded_file)
                
                # Strip whitespace from column names
                reader.fieldnames = [name.strip() for name in reader.fieldnames]
                
                required_columns = {'section_id', 'question_text', 'option_a', 'option_b',
                                  'option_c', 'option_d', 'correct_option', 'explanation_a',
                                  'explanation_b', 'explanation_c', 'explanation_d'}
                
                if not required_columns.issubset(reader.fieldnames):
                    missing = required_columns - set(reader.fieldnames)
                    messages.error(request, f'Missing columns: {", ".join(missing)}')
                    return redirect('upload_questions_csv')

                success_count = 0
                error_rows = []

                for i, row in enumerate(reader, start=2):  # Start counting from row 2 (header is row 1)
                    try:
                        section = Section.objects.get(section_id=row['section_id'])
                        Question.objects.create(
                            section=section,
                            question_text=row['question_text'],
                            option_a=row['option_a'],
                            option_b=row['option_b'],
                            option_c=row['option_c'],
                            option_d=row['option_d'],
                            correct_option=row['correct_option'].lower(),
                            explanation_a=row['explanation_a'],
                            explanation_b=row['explanation_b'],
                            explanation_c=row['explanation_c'],
                            explanation_d=row['explanation_d'],
                        )
                        success_count += 1
                    except Section.DoesNotExist:
                        error_rows.append(f"Row {i}: Section ID {row['section_id']} does not exist")
                    except KeyError as e:
                        error_rows.append(f"Row {i}: Missing required field - {str(e)}")
                    except Exception as e:
                        error_rows.append(f"Row {i}: {str(e)}")

                if success_count > 0:
                    messages.success(request, f'Successfully uploaded {success_count} questions!')
                if error_rows:
                    messages.warning(request, f'Errors in {len(error_rows)} rows. See details below.')
                    request.session['upload_errors'] = error_rows

                return redirect('upload_questions_csv')

            except Exception as e:
                messages.error(request, f'Error processing CSV file: {str(e)}')
                return redirect('upload_questions_csv')
    else:
        form = CSVUploadForm()

    upload_errors = request.session.pop('upload_errors', None)
    
    return render(request, 'upload_questions_csv.html', {
        'form': form,
        'upload_errors': upload_errors
    })
    
    

@login_required
def selected_courses(request):
    user_subjects = UserSubject.objects.filter(user=request.user)
    
    # Update selection status for each UserSubject instance
    for user_subject in user_subjects:
        user_subject.update_selection_status()
    
    context = {
        'user_subjects': user_subjects,
        'current_time': timezone.now(),
    }
    
    return render(request, 'selected_courses.html', context)


# eduPathCare/views.py

# @login_required
# def select_subjects(request):
#     if request.method == 'POST':
#         selected_subject_ids = request.POST.getlist('selected_subjects')
#         user = request.user

#         if not selected_subject_ids:
#             messages.error(request, 'Please select at least one subject to proceed.')
#             return redirect('subjects_list')

#         total_cost = 0

#         for subject_id in selected_subject_ids:
#             subject = Subject.objects.get(subject_id=subject_id)
#             total_cost += subject.price

#         if user.coins >= total_cost:
#             for subject_id in selected_subject_ids:
#                 subject = Subject.objects.get(subject_id=subject_id)
#                 if not UserSubject.objects.filter(user=user, subject=subject, is_selected=True).exists():
#                     UserSubject.objects.create(user=user, subject=subject, is_selected=True)
#                     user.coins -= subject.price
#                     user.save()
#                     # Log the subject selection activity
#                     UserActivity.objects.create(user=user, activity_type='subject_selected', details={'subject_id': subject.subject_id, 'subject_name': subject.subject_name})
#             messages.success(request, 'Your subjects have been successfully updated!')
#         else:
#             messages.error(request, 'You do not have enough coins to subscribe to these subjects.')
#             return redirect('purchase_coins')

#         return redirect('selected_courses')

#     return redirect('subjects_list')


# views.py
from datetime import timedelta  # Add this with other imports
from django.utils import timezone


@login_required
def select_subjects(request):
    if request.method == 'POST':
        selected_subject_ids = request.POST.getlist('selected_subjects')
        user = request.user

        if not selected_subject_ids:
            messages.error(request, 'Please select at least one subject to proceed.')
            return redirect('subjects_list')

        for subject_id in selected_subject_ids:
            subject = get_object_or_404(Subject, subject_id=subject_id)
            user_subject = UserSubject.objects.filter(user=user, subject=subject).first()

            if user_subject:
                if user_subject.renew_trial():
                    messages.info(request, f'Trial renewed for {subject.subject_name}')
            else:
                UserSubject.create_trial_subscription(user=user, subject=subject)
                messages.success(request, f'Free trial started for {subject.subject_name}')

        return redirect('selected_courses')
    return redirect('subjects_list')


    
@login_required
def view_selected_subject(request, subject_id):
    subject = get_object_or_404(Subject, pk=subject_id)
    first_section = subject.section_set.first()  # Get the first section for flashcards
    return render(request, 'view_selected_subject.html', {'subject': subject, 'section_id': first_section.section_id if first_section else None})


@login_required
def study_subject(request, subject_id):
    subject = get_object_or_404(Subject, pk=subject_id)
    sections = Section.objects.filter(subject=subject).prefetch_related('subsections')

    return render(request, 'study_subject.html', {'subject': subject, 'sections': sections})



@login_required
def final_exam(request, subject_id):
    subject = get_object_or_404(Subject, subject_id=subject_id)
    
    # Fetch all questions for the subject
    questions = Question.objects.filter(section__subject=subject)
    
    # Randomly select 50 questions without replacement
    questions = list(questions.order_by('?')[:50])  # Randomize and limit to 50 questions
    
    if not questions:
        messages.warning(request, "No questions available for this subject.")
        return redirect('view_selected_subject', subject_id=subject_id)
    
    # Prepare question data for the template
    question_data = [
        {
            'question_id': question.question_id,
            'question_text': question.question_text,
            'options': [
                {'value': 'a', 'text': question.option_a},
                {'value': 'b', 'text': question.option_b},
                {'value': 'c', 'text': question.option_c},
                {'value': 'd', 'text': question.option_d},
            ],
            'correct_option': question.correct_option,
        }
        for question in questions
    ]
    
    if request.method == 'POST':
        # Handle quiz submission
        score = 0
        results = []
        
        for question in questions:
            user_answer = request.POST.get(f'question_{question.question_id}')
            is_correct = user_answer == question.correct_option
            if is_correct:
                score += 1
            results.append({
                'question': question.question_text,
                'user_answer': user_answer,
                'correct_answer': question.correct_option,
                'is_correct': is_correct,
                'explanation': question.get_explanation(user_answer),
            })
        
        # Calculate time spent (if needed)
        time_spent = int(request.POST.get('time_spent', 1800))  # Default to 30 minutes
        minutes = time_spent // 60
        seconds = time_spent % 60
        
        # Save the final exam result
        final_exam, created = FinalExam.objects.get_or_create(
            user=request.user,
            subject=subject,
            defaults={
                'total_score': score,
                'attempts_count': 1,
                'completed_at': timezone.now(),
                'time_spent': time_spent
            }
        )
        
        # If the final exam already exists, update it
        if not created:
            final_exam.total_score = score
            final_exam.attempts_count += 1
            final_exam.completed_at = timezone.now()
            final_exam.time_spent = time_spent
            final_exam.save()
        
        # Update user progress (if needed)
        user_progress, created = UserProgress.objects.get_or_create(
            user=request.user,
            subject=subject,
            defaults={'completed_sections': [], 'total_score': 0}
        )
        
        # Optionally, mark the subject as completed if the user scores well
        if (score / len(questions)) * 100 >= 70:
            if subject.subject_id not in user_progress.completed_sections:
                user_progress.completed_sections.append(subject.subject_id)
                user_progress.total_score += score
                user_progress.save()
        
        # Render the results page using exam_results.html
        return render(request, 'exam_results.html', {
            'subject': subject,
            'results': results,
            'score': score,
            'total_questions': len(questions),
            'percentage_score': round((score / len(questions)) * 100, 2),
            'time_spent_minutes': minutes,
            'time_spent_seconds': seconds,
        })
    
    # Render the final exam form
    return render(request, 'final_exam.html', {
        'subject': subject,
        'question_data': question_data,  # Pass the structured question data
    })
    
    

from django.http import JsonResponse
from django.template.loader import render_to_string


@login_required
def load_section_content(request, content_id, content_type):
    """
    Load content for either a section or a subsection.
    :param content_id: The ID of the section or subsection.
    :param content_type: 'section' or 'subsection' to indicate the type of content.
    """
    if content_type == 'section':
        section = get_object_or_404(Section, section_id=content_id)
        content_html = render_to_string('section_content_partial.html', {
            'section': section,
            'subsection': None,  # Ensure subsections are NOT displayed when viewing section
        })
        return JsonResponse({'content': content_html, 'title': section.section_name,})

    elif content_type == 'subsection':
        subsection = get_object_or_404(Subsection, subsection_id=content_id)
        content_html = render_to_string('section_content_partial.html', {
            'section': None,  # Ensure section is NOT displayed when viewing subsection
            'subsection': subsection,
        })
        return JsonResponse({'content': content_html, 'title': subsection.subsection_name,})

    return JsonResponse({'error': 'Invalid content type'}, status=400)




# views.py
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from gtts import gTTS
import io

@csrf_exempt
def text_to_speech(request):
    if request.method == 'POST':
        text = request.POST.get('text', '')
        if text:
            # Generate audio in memory using gTTS
            tts = gTTS(text=text, lang='en')
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)

            # Stream the audio to the client
            response = HttpResponse(audio_buffer, content_type='audio/mpeg')
            response['Content-Disposition'] = 'inline; filename="speech.mp3"'
            return response
        else:
            return HttpResponse('No text provided', status=400)
    return HttpResponse('Invalid request method', status=405)
















@login_required
def load_quiz_content(request, section_id):
    section = get_object_or_404(Section, section_id=section_id)
    questions = Question.objects.filter(section=section).values(
        'question_id', 'question_text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_option'
    )
    
    return JsonResponse({
        'section_name': section.section_name,
        'questions': list(questions),  # Convert QuerySet to a list
    })

   
def sections_list_quiz(request, subject_id):
    subject = get_object_or_404(Subject, subject_id=subject_id)  # Fetch the subject
    sections = Section.objects.filter(subject=subject)  # Get sections under the subject
    return render(request, 'section_list_quiz.html', {
        'sections': sections,
        'subject_name': subject.subject_name,  # Pass the subject name
        'subject': subject  # Pass the subject object
    })


from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

@login_required
@require_POST
@csrf_exempt
def mark_as_completed(request):
    content_type = request.POST.get('content_type')  # 'section' or 'subsection'
    content_id = request.POST.get('content_id')     # ID of the section or subsection

    if not content_type or not content_id:
        return JsonResponse({'status': 'error', 'message': 'Missing content_type or content_id'}, status=400)

    try:
        if content_type == 'section':
            section = get_object_or_404(Section, section_id=content_id)
            section.is_completed = True
            section.save()
            return JsonResponse({'status': 'success', 'message': 'Section marked as completed'})

        elif content_type == 'subsection':
            subsection = get_object_or_404(Subsection, subsection_id=content_id)
            subsection.is_completed = True
            subsection.save()
            return JsonResponse({'status': 'success', 'message': 'Subsection marked as completed'})

        return JsonResponse({'status': 'error', 'message': 'Invalid content type'}, status=400)

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    
# Define coin packages (coins: price in dollars)
COIN_PACKAGES = {
    5: 100,   # 5 coins for $1
    10: 200,  # 10 coins for $2
    50: 1000,  # 50 coins for $5
    100: 2000,  # 100 coins for $10
}

@login_required
def purchase_coins(request):
    if request.method == 'POST':
        selected_coins = int(request.POST.get('selected_coins', 0))
        if selected_coins in COIN_PACKAGES:
            # In a real-world scenario, you would integrate with a payment gateway here.
            # For now, we'll just add the coins to the user's account.
            request.user.coins += selected_coins
            request.user.save()
            messages.success(request, f'Successfully purchased {selected_coins} coins!')
            return redirect('subjects_list')
        else:
            messages.error(request, 'Invalid coin package selected.')
    return render(request, 'purchase_coins.html', {'coin_packages': COIN_PACKAGES})




# Add to views.py
from .models import Payment
from .forms import PaymentForm, PaymentStatusForm

@login_required
def payment_details(request, coins, price):
    if request.method == 'POST':
        form = PaymentForm(request.POST, request.FILES)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.user = request.user
            payment.coins_purchased = coins
            payment.amount_paid = price
            payment.save()
            
            messages.success(request, 'Your payment details have been submitted for verification.')
            return redirect('subjects_list')
    else:
        form = PaymentForm(initial={'coins_purchased': coins, 'amount_paid': price})

    return render(request, 'payment_details.html', {
        'form': form,
        'coins': coins,
        'price': price
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def payment_list(request):
    payments = Payment.objects.all().order_by('-transaction_date')
    return render(request, 'admin/payment_list.html', {'payments': payments})

@login_required
@user_passes_test(lambda u: u.is_staff)
def payment_detail(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    
    if request.method == 'POST':
        status_form = PaymentStatusForm(request.POST, instance=payment)
        if status_form.is_valid():
            updated_payment = status_form.save(commit=False)
            updated_payment.admin = request.user
            updated_payment.processed_at = timezone.now()
            updated_payment.save()
            
            # If payment is approved, add coins to user's account
            if updated_payment.status == 'approved':
                user = updated_payment.user
                user.coins += updated_payment.coins_purchased
                user.save()
                
                # Log the coin purchase activity
                UserActivity.objects.create(
                    user=user,
                    activity_type='coin_purchased',
                    details={
                        'coins': updated_payment.coins_purchased,
                        'amount': str(updated_payment.amount_paid),
                        'payment_id': updated_payment.id
                    }
                )
            
            messages.success(request, 'Payment status updated successfully!')
            return redirect('payment_detail', payment_id=payment_id)
    else:
        status_form = PaymentStatusForm(instance=payment)
    
    return render(request, 'admin/payment_detail.html', {
        'payment': payment,
        'status_form': status_form
    })




from trivia_game.models import GameSession

@login_required
def user_dashboard(request):
    # Fetch user progress and quiz performance from eduPathCare
    user_progress = UserProgress.objects.filter(user=request.user).select_related('subject')
    quizzes = Quiz.objects.filter(user=request.user).select_related('subject', 'section')
    
    # Calculate overall progress and performance
    total_sections_completed = sum(len(progress.completed_sections) for progress in user_progress)
    total_sections = Section.objects.count()
    overall_progress = (total_sections_completed / total_sections) * 100 if total_sections > 0 else 0

    # Fetch trivia game data
    trivia_sessions = GameSession.objects.filter(user=request.user)
    total_coins_won = sum(session.score for session in trivia_sessions)
    
    # Fetch purchased coins from the user's profile
    total_coins_purchased = request.user.coins

    # Prepare data for charts
    subject_performance = []
    for progress in user_progress:
        subject = progress.subject
        quizzes_for_subject = quizzes.filter(subject=subject)
        total_quizzes = quizzes_for_subject.count()
        correct_answers = sum(quiz.total_score for quiz in quizzes_for_subject)
        total_questions = Question.objects.filter(section__subject=subject).count()  # Fix: Directly use count()
        percentage_score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
        
        subject_performance.append({
            'subject': subject,
            'total_questions': total_questions,  # Add total questions
            'percentage_score': percentage_score,
            'suggest_improvement': percentage_score < 70  # Suggest improvement if score is below 70%
        })

    context = {
        'user_progress': user_progress,
        'overall_progress': overall_progress,
        'subject_performance': subject_performance,
        'total_coins_won': total_coins_won,
        'total_coins_purchased': total_coins_purchased,
    }

    return render(request, 'user_dashboard.html', context)


# eduPathCare/views.py
@login_required
def withdraw_coins(request):
    if request.method == 'POST':
        # Handle withdrawal logic here
        messages.success(request, 'Withdrawal request submitted successfully!')
        return redirect('user_dashboard')
    return redirect('user_dashboard')


from .models import Flashcard

@login_required
def flashcard_view(request, section_id):
    section = get_object_or_404(Section, section_id=section_id)
    flashcards = section.flashcards.all()
    return render(request, 'flashcard.html', {
        'section': section,
        'flashcards': flashcards
    })

@login_required
@require_POST
@csrf_exempt
def toggle_mastered(request, flashcard_id):
    flashcard = get_object_or_404(Flashcard, flashcard_id=flashcard_id)
    flashcard.is_mastered = not flashcard.is_mastered
    flashcard.save()
    return JsonResponse({'status': 'success', 'is_mastered': flashcard.is_mastered})


@login_required
def list_section_flashcards(request, subject_id):
    subject = get_object_or_404(Subject, subject_id=subject_id)
    sections = Section.objects.filter(subject=subject, flashcards__isnull=False).distinct()
    return render(request, 'list_section_flashcard.html', {
        'subject': subject,
        'sections': sections
    })
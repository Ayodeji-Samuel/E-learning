# eduPathCare/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import User, Subject, Section, Subsection, Question, Quiz, FinalExam, UserProgress, UserSubject, UserActivity
from trivia_game.models import Category, DifficultyLevel, CoinReward, GameSession, GameSessionQuestion
from .forms import SubjectForm, SectionForm, SubsectionForm, QuestionForm, QuizForm, FinalExamForm, UserForm, AdminQuizForm

@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_dashboard(request):
    # Fetch the first subject or any subject to pass its ID
    subject = Subject.objects.first()
    return render(request, 'admin_dashboard.html', {'subject_id': subject.subject_id if subject else None})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def manage_users(request):
    users = User.objects.all()
    return render(request, 'admin/manage_users.html', {'users': users})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def manage_subject(request):
    # Fetch all subjects
    subjects = Subject.objects.all()
    return render(request, 'admin/manage_subjects.html', {'subjects': subjects})


@login_required
def manage_subsection(request, section_id):
    section = get_object_or_404(Section, section_id=section_id)
    subsections = section.subsections.all()
    return render(request, 'admin/manage_subsections.html', {'section': section, 'subsections': subsections})



@login_required
@user_passes_test(lambda u: u.is_superuser)
def manage_sections(request, subject_id):
    subject = get_object_or_404(Subject, subject_id=subject_id)
    sections = Section.objects.filter(subject=subject)
    return render(request, 'admin/manage_sections.html', {'subject': subject, 'sections': sections})



@login_required
@user_passes_test(lambda u: u.is_superuser)
def manage_questions(request):
    questions = Question.objects.all()
    return render(request, 'admin/manage_questions.html', {'questions': questions})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def manage_quizzes(request):
    quizzes = Quiz.objects.all()
    return render(request, 'admin/manage_quizzes.html', {'quizzes': quizzes})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def manage_final_exams(request):
    final_exams = FinalExam.objects.all()
    return render(request, 'admin/manage_final_exams.html', {'final_exams': final_exams})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def manage_categories(request):
    categories = Category.objects.all()
    return render(request, 'admin/manage_categories.html', {'categories': categories})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def manage_difficulty_levels(request):
    difficulty_levels = DifficultyLevel.objects.all()
    return render(request, 'admin/manage_difficulty_levels.html', {'difficulty_levels': difficulty_levels})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def manage_coin_rewards(request):
    coin_rewards = CoinReward.objects.all()
    return render(request, 'admin/manage_coin_rewards.html', {'coin_rewards': coin_rewards})

# Add CRUD operations for each model here (create, update, delete)

# eduPathCare/views.py

@login_required
@user_passes_test(lambda u: u.is_superuser)
def create_user(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'User created successfully.')
            return redirect('manage_users')
    else:
        form = UserForm()
    return render(request, 'admin/create_user.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'User updated successfully.')
            return redirect('manage_users')
    else:
        form = UserForm(instance=user)
    return render(request, 'admin/edit_user.html', {'form': form, 'user': user})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    messages.success(request, 'User deleted successfully.')
    return redirect('manage_users')

#=========================Subjects==========================   
# eduPathCare/views.py

@login_required
@user_passes_test(lambda u: u.is_superuser)
def create_subject(request):
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subject created successfully.')
            return redirect('manage_subject')
    else:
        form = SubjectForm()
    return render(request, 'admin/create_subject.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def edit_subject(request, subject_id):
    subject = get_object_or_404(Subject, subject_id=subject_id)
    if request.method == 'POST':
        form = SubjectForm(request.POST, instance=subject)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subject updated successfully.')
            return redirect('manage_subject')
    else:
        form = SubjectForm(instance=subject)
    return render(request, 'admin/edit_subject.html', {'form': form, 'subject': subject})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def delete_subject(request, subject_id):
    subject = get_object_or_404(Subject, subject_id=subject_id)
    subject.delete()
    messages.success(request, 'Subject deleted successfully.')
    return redirect('manage_subject')


#=========================Subsections==========================
@login_required
def create_subsection(request, section_id):
    """
    View to create a new subsection for a given section.
    """
    section = get_object_or_404(Section, section_id=section_id)
    if request.method == 'POST':
        form = SubsectionForm(request.POST)
        if form.is_valid():
            subsection = form.save(commit=False)
            subsection.section = section
            subsection.save()
            messages.success(request, 'Subsection created successfully!')
            return redirect('manage_subsection', section_id=section.section_id)
    else:
        form = SubsectionForm()
    return render(request, 'admin/create_subsection.html', {'form': form, 'section': section})

@login_required
def edit_subsection(request, subsection_id):
    """
    View to edit an existing subsection.
    """
    subsection = get_object_or_404(Subsection, subsection_id=subsection_id)
    if request.method == 'POST':
        form = SubsectionForm(request.POST, instance=subsection)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subsection updated successfully!')
            return redirect('manage_subsection', section_id=subsection.section.section_id)
    else:
        form = SubsectionForm(instance=subsection)
    return render(request, 'admin/edit_subsection.html', {'form': form, 'subsection': subsection})

@login_required
def delete_subsection(request, subsection_id):
    """
    View to delete a subsection.
    """
    subsection = get_object_or_404(Subsection, subsection_id=subsection_id)
    section_id = subsection.section.section_id
    subsection.delete()
    messages.success(request, 'Subsection deleted successfully!')
    return redirect('manage_subsection', section_id=section_id)

# @login_required
# def manage_subsection(request, section_id):
#     """
#     View to manage subsections for a given section.
#     """
#     section = get_object_or_404(Section, section_id=section_id)
#     subsections = section.subsections.all()
#     return render(request, 'manage_subsection.html', {'section': section, 'subsections': subsections})

#=========================Questions==========================

@login_required
def create_question(request, section_id):
    section = get_object_or_404(Section, section_id=section_id)
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.section = section
            question.save()
            messages.success(request, 'Question created successfully.')
            return redirect('manage_sections', subject_id=section.subject.subject_id)
    else:
        form = QuestionForm()
    return render(request, 'create_quiz.html', {'form': form, 'section': section})

@login_required
def edit_question(request, question_id):
    question = get_object_or_404(Question, question_id=question_id)
    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            messages.success(request, 'Question updated successfully.')
            return redirect('manage_sections', subject_id=question.section.subject.subject_id)
    else:
        form = QuestionForm(instance=question)
    return render(request, 'edit_question.html', {'form': form, 'question': question})

@login_required
def delete_question(request, question_id):
    question = get_object_or_404(Question, question_id=question_id)
    section_id = question.section.section_id
    question.delete()
    messages.success(request, 'Question deleted successfully.')
    return redirect('manage_sections', subject_id=question.section.subject.subject_id)





#=========================Quiz==========================
# eduPathCare/views.py

@login_required
@user_passes_test(lambda u: u.is_superuser)
def create_quiz(request):
    if request.method == 'POST':
        form = AdminQuizForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Quiz created successfully.')
            return redirect('manage_quizzes')
    else:
        form = AdminQuizForm()
    return render(request, 'admin/create_quiz.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def edit_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, quiz_id=quiz_id)
    if request.method == 'POST':
        form = AdminQuizForm(request.POST, instance=quiz)
        if form.is_valid():
            form.save()
            messages.success(request, 'Quiz updated successfully.')
            return redirect('manage_quizzes')
    else:
        form = AdminQuizForm(instance=quiz)
    return render(request, 'admin/edit_quiz.html', {'form': form, 'quiz': quiz})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def delete_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, quiz_id=quiz_id)
    quiz.delete()
    messages.success(request, 'Quiz deleted successfully.')
    return redirect('manage_quizzes')

#=========================Final Exam==========================
# eduPathCare/views.py

@login_required
@user_passes_test(lambda u: u.is_superuser)
def create_final_exam(request):
    if request.method == 'POST':
        form = FinalExamForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Final Exam created successfully.')
            return redirect('manage_final_exams')
    else:
        form = FinalExamForm()
    return render(request, 'admin/create_final_exam.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def edit_final_exam(request, final_exam_id):
    final_exam = get_object_or_404(FinalExam, final_exam_id=final_exam_id)
    if request.method == 'POST':
        form = FinalExamForm(request.POST, instance=final_exam)
        if form.is_valid():
            form.save()
            messages.success(request, 'Final Exam updated successfully.')
            return redirect('manage_final_exams')
    else:
        form = FinalExamForm(instance=final_exam)
    return render(request, 'admin/edit_final_exam.html', {'form': form, 'final_exam': final_exam})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def delete_final_exam(request, final_exam_id):
    final_exam = get_object_or_404(FinalExam, final_exam_id=final_exam_id)
    final_exam.delete()
    messages.success(request, 'Final Exam deleted successfully.')
    return redirect('manage_final_exams')

#=========================Sections==========================

@login_required
@user_passes_test(lambda u: u.is_superuser)
def create_section(request, subject_id):
    subject = get_object_or_404(Subject, subject_id=subject_id)
    if request.method == "POST":
        form = SectionForm(request.POST, request.FILES)
        if form.is_valid():
            section = form.save(commit=False)
            section.subject = subject
            section.save()
            return redirect('subject_details', subject_id=subject.subject_id)
    else:
        form = SectionForm()
    return render(request, 'create_section.html', {'form': form, 'subject': subject})


@login_required
@user_passes_test(lambda u: u.is_superuser)
def delete_section(request, section_id):
    section = get_object_or_404(Section, section_id=section_id)
    subject_id = section.subject.subject_id
    section.delete()
    return redirect('subject_details', subject_id=subject_id)


@login_required
@user_passes_test(lambda u: u.is_superuser)
def edit_section(request, section_id):
    
    if request.user.role != 'mentor':
        messages.error(request, 'You do not have permission to edit sections.')
        return redirect('subjects_list')
    
    section = get_object_or_404(Section, section_id=section_id)
    subject = section.subject
    

    if request.method == "POST":
        form = SectionForm(request.POST, request.FILES, instance=section)
        if form.is_valid():
            form.save()
            messages.success(request, 'Section updated successfully!')

            return redirect('subject_details', subject_id=subject.subject_id)
    else:
        form = SectionForm(instance=section)

    return render(request, 'edit_section.html', {'form': form, 'subject': subject, 'section': section})


# eduPathCare/views_admin.py

@login_required
@user_passes_test(lambda u: u.is_superuser)
def view_user_activities(request):
    activities = UserActivity.objects.all().order_by('-timestamp')
    return render(request, 'admin/view_user_activities.html', {'activities': activities})
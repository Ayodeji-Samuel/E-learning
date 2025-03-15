#eduPathCare/urls.py

from django.urls import path, include
from .views import (
    signup_view, login_view, forgot_password_view, logout_view,
    subjects_list_view, subject_details_view, section_content_view,
    quiz_view, create_quiz, edit_question, delete_question, student_dashboard, index, ladderboard_view,
    upload_questions_csv, selected_courses, select_subjects, view_selected_subject, final_exam,
    study_subject, load_section_content, load_quiz_content, sections_list_quiz, mark_as_completed, purchase_coins,
    user_dashboard, withdraw_coins, dashboard_view, flashcard_view, toggle_mastered, list_section_flashcards, text_to_speech,
)


urlpatterns = [
    path('', index, name='index'),
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('forgot-password/', forgot_password_view, name='forgot_password'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('subjects/', subjects_list_view, name='subjects_list'),
    path('subjects/<int:subject_id>/', subject_details_view, name='subject_details'),
    path('sections/<int:section_id>/', section_content_view, name='section_content'),    
    
    path('quiz/<int:section_id>/', quiz_view, name='quiz'),
    path('create-quiz/<int:section_id>/', create_quiz, name='create_quiz'),
    path('edit-question/<int:question_id>/', edit_question, name='edit_question'),
    path('delete-question/<int:question_id>/', delete_question, name='delete_question'),
    path('student-dashboard/', student_dashboard, name='student_dashboard'),
    path('ladderboard/', ladderboard_view, name='ladderboard'),
    path('upload-questions-csv/', upload_questions_csv, name='upload_questions_csv'),
    path('selected-courses/', selected_courses, name='selected_courses'),
    path('select-subjects/', select_subjects, name='select_subjects'),
    
    
    path('subject/<int:subject_id>/', view_selected_subject, name='view_selected_subject'),
    path('subject/<int:subject_id>/study/', study_subject, name='study_subject'),
    #path('subject/<int:subject_id>/quiz/', take_quiz, name='take_quiz'),
    path('subject/<int:subject_id>/exam/', final_exam, name='final_exam'),
    #path('section/<int:content_id>/content/', load_section_content, name='load_section_content'),
    path('section/<int:content_id>/content/<str:content_type>/', load_section_content, name='load_section_content'),
    path('quiz/section/<int:section_id>/', load_quiz_content, name='load_quiz_content'),
    #path('submit-quiz/', submit_quiz, name='submit_quiz'),
    path('sections-quiz/<int:subject_id>/sections/', sections_list_quiz, name='sections_list_quiz'),
    path('mark_as_completed/', mark_as_completed, name='mark_as_completed'),
    path('purchase-coins/', purchase_coins, name='purchase_coins'),
    #path('paystack/callback/', paystack_callback, name='paystack_callback'),
    path('user-dashboard/', user_dashboard, name='user_dashboard'),
    path('withdraw-coins/', withdraw_coins, name='withdraw_coins'),
    
    path('section/<int:section_id>/flashcards/', flashcard_view, name='flashcards'),
    path('flashcard/<int:flashcard_id>/toggle-mastered/', toggle_mastered, name='toggle_mastered'),
    path('subject/<int:subject_id>/flashcards/', list_section_flashcards, name='list_section_flashcards'),
    
    path('text-to-speech/', text_to_speech, name='text_to_speech'),
]

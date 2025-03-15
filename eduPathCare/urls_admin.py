# eduPathCare/urls_admin.py

from django.urls import path
from .views_admin import (
    admin_dashboard, manage_users, manage_quizzes, manage_subject, manage_sections, manage_subsection,
    manage_questions, manage_final_exams, manage_categories, manage_difficulty_levels, manage_coin_rewards, create_user,
    edit_user, delete_user, create_subject, edit_subject, delete_subject, create_subsection, edit_subsection,
    delete_subsection, create_quiz, edit_quiz, delete_quiz, create_final_exam, edit_final_exam, delete_final_exam, create_section, delete_section, edit_section,
    create_question, edit_question, delete_question, view_user_activities,
)
from trivia_game.views_admin import create_category, edit_category, delete_category, create_difficulty_level, edit_difficulty_level, delete_difficulty_level, create_coin_reward, edit_coin_reward, delete_coin_reward

urlpatterns = [
    path('dashboard/', admin_dashboard, name='admin_dashboard'),
    path('users/', manage_users, name='manage_users'),
    #path('subjects/', manage_subject, name='manage_subject'),
    path('subjects/', manage_subject, name='manage_subject'),
    path('sections/<int:subject_id>/', manage_sections, name='manage_sections'),
    path('subsections/<int:section_id>/', manage_subsection, name='manage_subsection'),
    #path('subsections/', manage_subsection, name='manage_subsection'),
    path('questions/', manage_questions, name='manage_questions'),
    path('quizzes/', manage_quizzes, name='manage_quizzes'),
    path('final-exams/', manage_final_exams, name='manage_final_exams'),
    path('categories/', manage_categories, name='manage_categories'),
    path('difficulty-levels/', manage_difficulty_levels, name='manage_difficulty_levels'),
    path('coin-rewards/', manage_coin_rewards, name='manage_coin_rewards'),
    
    path('users/create/', create_user, name='create_user'),
    path('users/edit/<int:user_id>/', edit_user, name='edit_user'),
    path('users/delete/<int:user_id>/', delete_user, name='delete_user'),
    
    path('subjects/create/', create_subject, name='create_subject'),
    path('subjects/edit/<int:subject_id>/', edit_subject, name='edit_subject'),
    path('subjects/delete/<int:subject_id>/', delete_subject, name='delete_subject'),
    
    path('create-section/<int:subject_id>/', create_section, name='create_section'),
    path('edit-section/<int:section_id>/', edit_section, name='edit_section'),
    path('delete-section/<int:section_id>/', delete_section, name='delete_section'),
        
  
    path('create-subsection/<int:section_id>/', create_subsection, name='create_subsection'),
    path('edit-subsection/<int:subsection_id>/', edit_subsection, name='edit_subsection'),
    path('delete-subsection/<int:subsection_id>/', delete_subsection, name='delete_subsection'),

    
    path('create-question/<int:section_id>/', create_question, name='create_question'),
    path('edit-question/<int:question_id>/', edit_question, name='edit_question'),
    path('delete-question/<int:question_id>/', delete_question, name='delete_question'),
    
    path('quizzes/create/', create_quiz, name='create_quiz'),
    path('quizzes/edit/<int:quiz_id>/', edit_quiz, name='edit_quiz'),
    path('quizzes/delete/<int:quiz_id>/', delete_quiz, name='delete_quiz'),
    
    path('final-exams/create/', create_final_exam, name='create_final_exam'),
    path('final-exams/edit/<int:final_exam_id>/', edit_final_exam, name='edit_final_exam'),
    path('final-exams/delete/<int:final_exam_id>/', delete_final_exam, name='delete_final_exam'),
    
    path('categories/create/', create_category, name='create_category'),
    path('categories/edit/<int:category_id>/', edit_category, name='edit_category'),
    path('categories/delete/<int:category_id>/', delete_category, name='delete_category'),

    path('difficulty-levels/create/', create_difficulty_level, name='create_difficulty_level'),
    path('difficulty-levels/edit/<int:difficulty_level_id>/', edit_difficulty_level, name='edit_difficulty_level'),
    path('difficulty-levels/delete/<int:difficulty_level_id>/', delete_difficulty_level, name='delete_difficulty_level'),

    path('coin-rewards/create/', create_coin_reward, name='create_coin_reward'),
    path('coin-rewards/edit/<int:coin_reward_id>/', edit_coin_reward, name='edit_coin_reward'),
    path('coin-rewards/delete/<int:coin_reward_id>/', delete_coin_reward, name='delete_coin_reward'),
    
    path('admin/view_user_activities/', view_user_activities, name='view_user_activities'),
]
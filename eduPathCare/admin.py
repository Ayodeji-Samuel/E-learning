from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User, Subject, Section, Question, Quiz, UserProgress, UserSubject, Subsection, Flashcard
)




# Custom User Admin
class CustomUserAdmin(UserAdmin):
    list_display = ('user_id', 'username', 'email', 'role', 'created_at', 'coins')
    list_filter = ('user_id', 'username', 'email', 'role')
    filter_horizontal = ()
    exclude = ('is_active',)
    #search_fields = ('username', 'email')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'profile_picture', 'bio', 'role')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
        ('Coins', {'fields': ('coins',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role')
        }),
    )
    ordering = ('email',)
    

class CustomQuestionAdmin(admin.ModelAdmin):
    list_display = ('question_id', 'question_text', 'correct_option', 'section')
    
    
class CustomSectionAdmin(admin.ModelAdmin):
    list_display = ('section_id', 'section_name', 'subject')
    
    
# Registering Models
admin.site.register(User, CustomUserAdmin)
admin.site.register(Subject)
admin.site.register(Section, CustomSectionAdmin)
admin.site.register(Question, CustomQuestionAdmin)
admin.site.register(Quiz)
admin.site.register(UserProgress)
admin.site.register(UserSubject)
admin.site.register(Subsection)
admin.site.register(Flashcard)
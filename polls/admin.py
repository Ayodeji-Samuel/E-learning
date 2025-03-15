from django.contrib import admin
from .models import Poll, Option, Participant, TextResponse

# Inline for Option model (to display options within the Poll admin page)
class OptionInline(admin.TabularInline):
    model = Option
    extra = 1  # Number of empty option forms to display

# Inline for TextResponse model (to display responses within the Poll admin page)
class TextResponseInline(admin.TabularInline):
    model = TextResponse
    extra = 0  # No empty response forms by default
    readonly_fields = ('participant', 'response', 'created_at')  # Make fields read-only

# Poll Admin Configuration
@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    list_display = ('question', 'creator', 'question_type', 'is_active', 'expiration_time', 'created_at')
    list_filter = ('is_active', 'question_type', 'creator')
    search_fields = ('question', 'creator__username')
    inlines = [OptionInline, TextResponseInline]  # Include options and responses in the Poll admin page
    fieldsets = [
        (None, {'fields': ['creator', 'question', 'question_type']}),
        ('Activation', {'fields': ['is_active', 'expiration_time']}),
    ]

# Option Admin Configuration
@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    list_display = ('text', 'poll', 'votes')
    list_filter = ('poll',)
    search_fields = ('text', 'poll__question')

# Participant Admin Configuration
@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('identifier', 'poll', 'has_responded', 'created_at')
    list_filter = ('poll', 'has_responded')
    search_fields = ('identifier', 'poll__question')

# TextResponse Admin Configuration
@admin.register(TextResponse)
class TextResponseAdmin(admin.ModelAdmin):
    list_display = ('poll', 'participant', 'response', 'is_active', 'expiration_time', 'created_at')
    list_filter = ('poll', 'is_active')
    search_fields = ('response', 'poll__question')
    list_editable = ('is_active',)  # Allow toggling is_active directly from the list view
    fieldsets = [
        (None, {'fields': ['poll', 'participant', 'response']}),
        ('Activation', {'fields': ['is_active', 'expiration_time']}),
    ]
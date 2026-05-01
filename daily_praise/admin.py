from django.contrib import admin
from .models import KudosNote, WeeklyReview

@admin.register(KudosNote)
class KudosNoteAdmin(admin.ModelAdmin):
    list_display = ('note_id', 'user', 'updated_at', 'is_active')
    search_fields = ('praise_content',)

@admin.register(WeeklyReview)
class WeeklyReviewAdmin(admin.ModelAdmin):
    list_display = ('review_id', 'user', 'updated_at', 'review_start_date', 'review_end_date', 'is_active')
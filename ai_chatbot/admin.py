from django.contrib import admin
from .models import ChatSession, AIChatLog, SOSLog, AIModelRegistry, SystemPrompt

@admin.register(AIModelRegistry)
class AIModelAdmin(admin.ModelAdmin):
    list_display = ('model_id', 'model_name', 'model_type', 'updated_at', 'is_active')
    list_filter = ('is_active', 'model_type', 'created_at', 'updated_at')
    search_fields = ('model_name',)
    
@admin.register(SystemPrompt)
class SystemPromptAdmin(admin.ModelAdmin):
    list_display = ('prompt_id', 'prompt_name', 'updated_at', 'created_at', 'is_active')
    list_filter = ('is_active', 'created_at', 'updated_at')
    search_fields = ('prompt_name', 'content', 'version_note',)

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'user', 'created_at', 'last_activity', 'is_active')
    list_filter = ('is_active', 'created_at', 'last_activity')
    search_fields = ('session_summary',)
    
@admin.register(AIChatLog)
class AIChatLogAdmin(admin.ModelAdmin):
    list_display = ('chat_log_id', 'user', 'session', 'sender', 'timestamp')
    list_filter = ('sender', 'llm_model', 'timestamp')
    search_fields = ('message_content',)

@admin.register(SOSLog)
class SOSLogAdmin(admin.ModelAdmin):
    list_display = ('sos_id', 'user', 'chat_log', 'triggering_keyword', 'timestamp')
    list_filter = ('action_taken',)

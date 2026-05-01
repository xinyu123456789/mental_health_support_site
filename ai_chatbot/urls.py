from django.urls import path
from . import views

app_name = 'ai_chatbot'

urlpatterns = [
    path('chat/', views.chat_page_view, name='chat_page'),
    path('api/history/', views.get_chat_history_api, name='api_history'),
    path('api/send/', views.send_message_stream_api, name='api_send'),
]
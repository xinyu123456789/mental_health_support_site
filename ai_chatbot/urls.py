from django.urls import path
from . import views

app_name = 'ai_chatbot'

urlpatterns = [
    # 網頁入口： /ai_chatbot/chat/
    path('chat/', views.chat_page_view, name='chat_page'),
    
    # API 入口一： /ai_chatbot/api/history/
    path('api/history/', views.get_chat_history_api, name='api_history'),
    
    # API 入口二： /ai_chatbot/api/send/
    path('api/send/', views.send_message_stream_api, name='api_send'),
]
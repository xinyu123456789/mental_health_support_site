from django.urls import path
from . import views

# 設定 app_name 有助於在 Django Template 中使用 {% url 'app_name:name' %} 來反向解析網址
app_name = 'daily_praise' 

urlpatterns = [
    # 使用者訪問的頁面路由 (例如：http://127.0.0.1:8000/kudos/)
    path('kudos/', views.kudos_note_page, name='kudos_note_page'),
    path('kudos/success/', views.kudos_success_page, name='kudos_success_page'),
    # 前端 JavaScript Fetch 呼叫的 API 路由，需與 JS 中的 URL 對應
    path('api/kudos/create/', views.create_kudos_api, name='create_kudos_api'),
]
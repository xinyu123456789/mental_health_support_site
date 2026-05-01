from django.urls import path
from . import views

app_name = 'daily_praise' 

urlpatterns = [
    path('kudos/', views.kudos_note_page, name='kudos_note_page'),
    path('kudos/success/', views.kudos_success_page, name='kudos_success_page'),
    path('api/kudos/create/', views.create_kudos_api, name='create_kudos_api'),
]
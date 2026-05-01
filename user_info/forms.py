from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class CustomUserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        # 因為你的模型規定 email 是登入帳號，username 是必填
        # 所以註冊時這兩個欄位都要讓用戶填寫
        fields = ('email', 'username')
        
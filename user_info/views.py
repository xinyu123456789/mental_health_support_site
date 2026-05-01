from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import CustomUserRegisterForm

def register_view(request):
    """處理使用者註冊"""
    if request.method == 'POST':
        form = CustomUserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('core:home') 
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
    else:
        form = CustomUserRegisterForm()
        
    return render(request, 'user_info/register.html', {'form': form})

def login_view(request):
    """處理使用者登入"""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('core:home')
        else:
            messages.error(request, "帳號或密碼輸入錯誤，請再試一次。")
    else:
        form = AuthenticationForm()
        
    return render(request, 'user_info/login.html', {'form': form})

def logout_view(request):
    """處理使用者登出"""
    logout(request)
    return redirect('user_info:login')
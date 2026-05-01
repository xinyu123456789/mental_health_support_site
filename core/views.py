from django.shortcuts import render

def home_view(request):
    """渲染系統主頁 (大廳)"""
    return render(request, 'core/home.html')
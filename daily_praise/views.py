import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import KudosNote

@login_required
def kudos_note_page(request):
    """
    渲染每日誇誇筆記的前端頁面
    """
    return render(request, 'daily_praise/kudos_note.html')

@login_required
def kudos_success_page(request):
    """渲染紀錄成功的畫面"""
    return render(request, 'daily_praise/kudos_success.html')

@login_required
@require_POST
def create_kudos_api(request):
    """
    接收前端 AJAX (Fetch API) 傳來的誇誇內容，並存入資料庫
    """
    try:
        # 解析前端傳來的 JSON 資料
        data = json.loads(request.body)
        content = data.get('praise_content', '').strip()
        
        # 基本的後端驗證：確保內容不為空
        if not content:
            return JsonResponse({'error': '誇誇內容不能為空喔！'}, status=400)
            
        secure_content = content 

        # 建立 KudosNote 紀錄
        KudosNote.objects.create(
            user=request.user,
            praise_content=secure_content,
        )
        
        return JsonResponse({'message': '太棒了！你的誇誇已經妥善保存。'}, status=201)
        
    except json.JSONDecodeError:
        return JsonResponse({'error': '資料格式錯誤'}, status=400)
    except Exception as e:
        print(f"Error creating KudosNote: {e}")
        return JsonResponse({'error': '系統發生預期外的錯誤，請稍後再試。'}, status=500)
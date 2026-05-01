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
            
        # ==========================================
        # 【資安提醒】依據系統設計，個人日記需進行適度加密[cite: 1]
        # 在這裡實作 AES 加密邏輯，確保寫入資料庫的內容為密文
        # ==========================================
        # from your_encryption_module import encrypt_data
        # encrypted_content = encrypt_data(content)
        
        # 為了展示，這裡先寫入原始字串（建議替換為 encrypted_content）
        secure_content = content 

        # 建立 KudosNote 紀錄
        KudosNote.objects.create(
            user=request.user,                # 自動綁定當前登入用戶[cite: 3]
            praise_content=secure_content,    # 寫入內容[cite: 3]
            # mood_score 預設為 5，若未來前端有傳遞也可在此接收[cite: 3]
        )
        
        return JsonResponse({'message': '太棒了！你的誇誇已經妥善保存。'}, status=201)
        
    except json.JSONDecodeError:
        return JsonResponse({'error': '資料格式錯誤'}, status=400)
    except Exception as e:
        # 記錄錯誤日誌 (Log) 供後續除錯，回傳通用錯誤訊息給前端
        print(f"Error creating KudosNote: {e}")
        return JsonResponse({'error': '系統發生預期外的錯誤，請稍後再試。'}, status=500)
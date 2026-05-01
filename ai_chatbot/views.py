import json
import urllib.parse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import ChatSession, AIChatLog, SOSLog, SystemPrompt, AIModelRegistry
from .service.llm_client import LLMClient, NLPClient
from django.http import JsonResponse, StreamingHttpResponse

@login_required 
def chat_page_view(request):
    """只負責渲染聊天室網頁外殼與側邊欄"""
    history_sessions = ChatSession.objects.filter(
        user=request.user, 
        is_active=True
    ).order_by('-last_activity')
    
    context = {
        'page_title': '涵涵 - 你的專屬 AI 陪伴',
        'history_sessions': history_sessions,
        'first_chat': '你好！我是涵涵，今天想跟我分享什麼呢？',
    }
    return render(request, 'ai_chatbot/index.html', context)

@login_required  
def get_chat_history_api(request):
    """只負責撈取舊對話紀錄並回傳 JSON"""
    if request.method == 'GET':
        session_id = request.GET.get('session_id')
        if not session_id:
            return JsonResponse({'status': 'ERROR', 'message': '缺少 session_id'}, status=400)

        # 確保這個 session 是這個用戶的
        session = get_object_or_404(ChatSession, session_id=session_id, user=request.user, is_active=True)
        logs = AIChatLog.objects.filter(session=session).order_by('timestamp')
        
        messages = []
        for log in logs:
            messages.append({
                'sender': log.sender, 
                'content': log.message_content
            })
            
        return JsonResponse({'status': 'SUCCESS', 'messages': messages})
    
    return JsonResponse({'status': 'ERROR', 'message': '不支援的請求方法'}, status=405)

@login_required
def send_message_stream_api(request):
    """負責處理發送訊息、SOS 檢查、呼叫 LLM 與回傳串流"""
    if request.method == 'POST':
        try:
            NORMAL_PROMPT_ID = 1      
            EMERGENCY_PROMPT_ID = 2   
            
            data = json.loads(request.body)
            user_message = data.get('message', '').strip()
            session_id = data.get('session_id')

            if not user_message:
                return JsonResponse({'status': 'ERROR', 'message': '訊息不能為空喔！'}, status=400)
            
            if session_id:
                session = get_object_or_404(ChatSession, session_id=session_id, user=request.user, is_active=True)
            else:
                session = ChatSession.objects.create(
                    user=request.user,
                    session_summary=user_message[:15] + "..."
                )
            
            raw_history = AIChatLog.objects.filter(session=session).order_by('-timestamp')[:5]
            history_for_api = []
            for log in reversed(raw_history):
                role = 'user' if log.sender == 'user' else 'assistant' 
                history_for_api.append({'role': role, 'content': log.message_content})
            
            nlp_client = NLPClient()
            result = nlp_client.generate_reply(history_logs = history_for_api, current_message = user_message)
            
            emotional_score , keyword = result.split('\n')
            emotional_score = int(emotional_score.replace('Emotional Score: ', ''))
            keyword = keyword.replace('Key word: ', '')
            
            if emotional_score < 2:
                is_emergency = True
            else:
                is_emergency = False
            
            if is_emergency:
                active_prompt = SystemPrompt.objects.filter(pk=EMERGENCY_PROMPT_ID).first()
            else:
                active_prompt = SystemPrompt.objects.filter(pk=NORMAL_PROMPT_ID).first()
                if not active_prompt:
                    active_prompt = SystemPrompt.objects.filter(is_active=True).first()
            
            active_llm = AIModelRegistry.objects.filter(
                model_type=AIModelRegistry.ModelTypeChoice.LLM, 
                is_active=True
            ).first()
            active_nlp_model = AIModelRegistry.objects.filter(
                model_type=AIModelRegistry.ModelTypeChoice.NLP,
                is_active=True
            ).first()
            
            user_log = AIChatLog.objects.create(
                user=request.user,
                session=session,
                system_prompt=active_prompt,  
                llm_model=active_llm, 
                nlp_model=active_nlp_model,
                message_content=user_message,
                sender=AIChatLog.RoleChoices.USER,
                sentiment_score=emotional_score,
            )
            
            if is_emergency:
                SOSLog.objects.create(
                    user=request.user,
                    chat_log=user_log,
                    triggering_keyword=keyword,
                    action_taken=SOSLog.WarningActionTags.PROMPT_SWITCH 
                )

            llm_client = LLMClient()
            system_prompt = active_prompt.content if active_prompt else "你是一個溫馨的心理陪伴機器人，名叫涵涵。"
            
            def stream_response_generator():
                full_reply = ""
                for token in llm_client.generate_stream_reply(
                    system_prompt=system_prompt,
                    history_logs=history_for_api,
                    current_message=user_message
                ):
                    full_reply += token
                    yield token  

                AIChatLog.objects.create(
                    user=request.user,
                    session=session,
                    system_prompt=active_prompt,
                    llm_model=active_llm,
                    message_content=full_reply,
                    sender=AIChatLog.RoleChoices.AI
                )
                session.save()

            response = StreamingHttpResponse(stream_response_generator(), content_type='text/plain; charset=utf-8')
            response['X-Session-ID'] = str(session.session_id)
            response['X-Session-Summary'] = urllib.parse.quote(session.session_summary or "新對話")
            
            return response

        except json.JSONDecodeError:
            return JsonResponse({'status': 'ERROR', 'message': '資料格式錯誤'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'ERROR', 'message': f'系統發生錯誤：{str(e)}'}, status=500)
            
    return JsonResponse({'status': 'ERROR', 'message': '不支援的請求方法'}, status=405)
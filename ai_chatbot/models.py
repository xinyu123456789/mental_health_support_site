from django.db import models
from django.conf import settings

class AIModelRegistry(models.Model):
    '''紀錄系統使用的 AI 模型版本歷史'''
    class ModelTypeChoice(models.TextChoices):
        LLM = 'llm', '對話模型 (LLM)'
        NLP = 'nlp', '情緒分析模型 (NLP)'
        
    model_id = models.BigAutoField(verbose_name = '模型 ID', editable = False, primary_key = True)
    model_type = models.CharField(max_length = 10, choices = ModelTypeChoice.choices, verbose_name = '模型用途')
    model_name = models.CharField(max_length = 200, verbose_name = '模型名稱', help_text = '請填完整模型名稱 (名字＋版本，例如 TAIDE-8B)')
    is_active = models.BooleanField(default = True, db_index = True,  verbose_name = '是否為當前使用中', help_text = '只有一個模型會處於 True 的狀態')
    created_at = models.DateTimeField(auto_now_add = True, verbose_name = '模型上線時間')
    updated_at = models.DateTimeField(auto_now = True, verbose_name = '最後更新時間')
    
    class Meta:
        verbose_name = 'AI 模型'
        verbose_name_plural = '模型清單'
        ordering = ['-is_active', '-updated_at', 'model_type']
    
    def save(self, *args, **kwargs):
        if self.is_active:
            # 當這個模型要啟用時，先把同類型的其他模型都設為不啟用
            AIModelRegistry.objects.filter(model_type = self.model_type, is_active = True).exclude(pk = self.pk).update(is_active = False)
        super().save(*args, **kwargs)
    
    def __str__(self):
        time_str = self.created_at.strftime('%Y-%m-%d') if self.created_at else "尚未上線"
        return f"模型分類：{self.get_model_type_display()}，名稱： {self.model_name}，啟用狀態：{self.is_active}，創建時間：{time_str}"

class SystemPrompt(models.Model):
    '''儲存不同版本的 AI 人格設定指令'''
    prompt_id = models.BigAutoField(verbose_name = 'System Prompt ID', editable = False, primary_key = True)
    prompt_name = models.CharField(max_length = 100, verbose_name = "版本名稱", help_text = "例如：溫暖陪伴版 v1.1")
    content = models.TextField(verbose_name = "指令內容")
    is_active = models.BooleanField(default = False, verbose_name = "是否為當前使用中", help_text = "系統會抓取此欄位為 True 的指令來與用戶對話")
    version_note = models.CharField(max_length = 200, verbose_name = "更新說明", blank = True)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    
    class Meta:
        verbose_name = 'System Prompt'
        verbose_name_plural = 'System Prompt 清單'
        ordering = ['-is_active', '-updated_at', '-prompt_id']
        
    def save(self, *args, **kwargs):
        if self.is_active:
            # 把其他所有的 Prompt 都關掉
            SystemPrompt.objects.filter(is_active = True).exclude(pk = self.pk).update(is_active = False)
        super().save(*args, **kwargs)

    def __str__(self):
        time_str = self.created_at.strftime('%Y-%m-%d') if self.created_at else "尚未上線"
        active_status = "【使用中】" if self.is_active else "【未使用】"
        return f"{active_status}{self.prompt_name} ({time_str})"

class ChatSession(models.Model):
    '''AI 聊天對話階段，組裝聊天紀錄用'''
    session_id = models.BigAutoField(verbose_name = 'Session ID', help_text = '不要給我亂動', editable = False, primary_key = True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE, verbose_name = '關聯用戶', related_name = 'chat_sessions')
    last_activity = models.DateTimeField(auto_now = True, verbose_name = '最後一輪對話完成時間')
    session_summary = models.TextField(verbose_name = '當前對話階段摘要', help_text = '這個之後會用 LLM 自動摘要，不用管', blank = True, null = True)
    created_at = models.DateTimeField(auto_now_add = True, verbose_name = '階段創建時間(對話開始時間)')
    is_active = models.BooleanField(default = True, db_index = True,  verbose_name = '是否啟用這段對話紀錄(有沒有被刪除)', help_text = '讓用戶選擇要不要刪掉聊天紀錄')
    
    class Meta:
        verbose_name = '聊天階段'
        verbose_name_plural = '聊天階段清單'
        ordering = ['-last_activity', '-user', '-session_id']
        
    def __str__(self):
        display_summary = self.session_summary[:50] if self.session_summary else "新對話 (尚無摘要)"
        time_str = self.created_at.strftime('%Y-%m-%d') if self.created_at else "尚未上線"
        return f"Session ID：{self.session_id}，User ID：{self.user_id}，Summary：{display_summary}，創建時間：{time_str}"

class AIChatLog(models.Model):
    '''真正存聊天內容的，一句一句給 ID 儲存'''
    class RoleChoices(models.TextChoices):
        USER = 'user', '用戶'
        AI = 'assistant', '機器人'
    
    chat_log_id = models.BigAutoField(verbose_name = '訊息 ID', help_text = '不要亂弄喔', editable = False, primary_key = True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE, verbose_name = '關聯用戶', related_name = 'ai_chat_logs')
    session = models.ForeignKey('ChatSession', on_delete = models.CASCADE, verbose_name = '關聯對話階段', related_name = 'messages')
    system_prompt = models.ForeignKey('SystemPrompt', on_delete=models.RESTRICT, null=True, blank=True, verbose_name='關聯指令版本',related_name='logs')
    llm_model = models.ForeignKey('AIModelRegistry', on_delete = models.RESTRICT, verbose_name = '對話當下使用的模型', help_text = '這個不管用戶輸入或 LLM 回答都會記錄', null = True, blank = True, related_name = 'llm_chat_logs', limit_choices_to = {'model_type': 'llm'})
    nlp_model = models.ForeignKey('AIModelRegistry', on_delete = models.RESTRICT, verbose_name = '用來計算情緒分數的的 NLP 模型', help_text = '這個只計算用戶數入的情緒分數', null = True, blank = True, related_name = 'nlp_chat_logs', limit_choices_to = {'model_type': 'nlp'})
    message_content = models.TextField(verbose_name = '訊息內容')
    sender = models.CharField(max_length = 10, choices = RoleChoices.choices, default = RoleChoices.USER, verbose_name = '發送者角色')
    timestamp = models.DateTimeField(auto_now_add = True, verbose_name = '傳送時間', help_text = '用來排聊天順序')
    sentiment_score = models.FloatField(verbose_name = '此訊息的情緒分數', help_text = '用來做週總結的，如果是 LLM 的回覆就設成 null', null = True, blank = True)
    is_active = models.BooleanField(default = True, db_index = True,  verbose_name = '是否啟用這則訊息', help_text = '表示這則訊息有沒有被刪除')
    updated_at = models.DateTimeField(auto_now = True, verbose_name = '最後更新時間', help_text = '最後更新時間')
    
    class Meta:
        verbose_name = '聊天訊息'
        verbose_name_plural = '聊天訊息清單'
        ordering = ['timestamp', '-updated_at', '-chat_log_id']
        
    def __str__(self):
        content_preview = str(self.message_content)[:20] + "..." if self.message_content else "空訊息"
        time_str = self.timestamp.strftime('%Y-%m-%d') if self.timestamp else "尚未上線"
        model_name = self.llm_model.model_name if self.llm_model else "N/A"
        return f"訊息 ID：{self.chat_log_id}，角色：{self.sender}，內容：{content_preview}，回覆模型：{model_name}，傳送時間：{time_str}"

class SOSLog(models.Model):
    '''危機預警紀錄，這全部的東西都會自動產生，可以改的東西只有 Action'''
    class WarningActionTags(models.TextChoices):
        # --- Level 1：重度低落 / 危機 (極度負面) ---
        CRISIS_INTERVENTION = 'crisis_intv', '危機截斷 (暫停功能，導向外部專線)'
        CHAT_INVITE = 'chat_invite', '彈窗導引 (邀請用戶進入聊天室)'
        PROMPT_SWITCH = 'prompt_switch', '模式切換 (將涵涵切換為「深度陪伴」指令)'

        # --- Level 2：中度焦慮 / 挫折 (負面) ---
        PUSH_ARTICLE = 'push_article', '文章推薦 (推送情緒穩定或心理衛教文章)'
        PUSH_MEDIA = 'push_media', '影音推薦 (推送放鬆音樂或 Podcast)'
        PUSH_SCALE = 'push_scale', '量表引導 (建議進行心情溫度計 BSRS-5 測驗)'
        
        # --- 備用 ---
        MONITOR_ONLY = 'monitor', '僅標記監測 (不干擾用戶，但列入週報重點回顧)'
    
    sos_id = models.BigAutoField(verbose_name = '預警 ID', help_text = '動了會世界末日', editable = False, primary_key = True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name = '關聯用戶', on_delete = models.CASCADE, related_name = 'sos_logs')
    chat_log = models.OneToOneField('AIChatLog', verbose_name = '觸發預警的對話', on_delete = models.RESTRICT, related_name = 'triggered_sos')
    triggering_keyword = models.CharField(max_length = 200, verbose_name = '觸發預警的詞或句子', help_text = '這個會用 LLM 辨識再用程式處理，不要亂動')
    timestamp = models.DateTimeField(auto_now_add = True, verbose_name = '觸發預警時間')
    action_taken = models.CharField(max_length = 50, choices = WarningActionTags.choices, default = WarningActionTags.MONITOR_ONLY, verbose_name = '針對預警採取的動作標籤', help_text = '一開始會用模型快速判定，必要時管理員可調整')
    
    class Meta:
        verbose_name = '安全預警'
        verbose_name_plural = '預警清單'
        ordering = ['-timestamp', '-sos_id']
        
    def __str__(self):
        time_str = self.timestamp.strftime('%Y-%m-%d') if self.timestamp else "尚未上線"
        return f"預警 ID：{self.sos_id}，用戶 ID：{self.user_id}，動作：{self.get_action_taken_display()}，關鍵句：{self.triggering_keyword}，訊息 ID：{self.chat_log_id}，觸發時間：{time_str}"

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings

class KudosNote(models.Model):
    '''每日誇誇 or 成就紀錄'''
    note_id = models.BigAutoField(verbose_name = '誇誇 ID', editable = False, primary_key = True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE, verbose_name = '關聯用戶', related_name = 'kudos_notes')
    praise_content = models.TextField(verbose_name = '誇誇 or 成就內容', help_text = '對自己的讚美 or 成就感紀錄')
    mood_score = models.SmallIntegerField(verbose_name = '心情分數', default = 5, validators = [MinValueValidator(1), MaxValueValidator(10)], help_text = '1(極度低落) ~ 10(極度正向)')
    is_active = models.BooleanField(default = True, db_index = True,  verbose_name = '是否啟用')
    created_at = models.DateTimeField(auto_now_add = True, verbose_name = '誇誇創建時間')
    updated_at = models.DateTimeField(auto_now = True, verbose_name = '最後更新時間')

    class Meta:
        verbose_name = '誇誇'
        verbose_name_plural = '誇誇清單'
        ordering = ['-updated_at', '-created_at', '-note_id']

    def __str__(self):
        preview = self.praise_content[:30] + '...' if len(self.praise_content) > 30 else self.praise_content
        time_str = self.created_at.strftime('%Y-%m-%d') if self.created_at else "尚未上線"
        return f"誇誇 ID：{self.note_id}，創建者 ID：{self.user_id}，內容：{preview}，啟用狀態：{self.is_active}，創建時間：{time_str}"

class WeeklyReview(models.Model):
    '''週回顧報告'''
    review_id = models.BigAutoField(verbose_name = '報告 ID', editable = False, primary_key = True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE, verbose_name = '關聯用戶', related_name = 'weekly_reviews')
    review_start_date = models.DateField(verbose_name = '回顧起始日期', help_text = '週回顧的第一天')
    review_end_date = models.DateField(verbose_name = '回顧結束日期', help_text = '週回顧的第七天')
    summary_visualization_data = models.JSONField(default = list, verbose_name = '統計資料（json）', help_text = '儲存這週的所有資料，用 JSON 儲存')
    is_active = models.BooleanField(default = True, db_index = True,  verbose_name = '是否啟用', help_text = '可以拿來讓用戶選擇是否要顯示，或是管理員軟刪除')
    created_at = models.DateTimeField(auto_now_add = True, verbose_name = '報告創建時間')
    updated_at = models.DateTimeField(auto_now = True, verbose_name = '最後更新時間')
    
    class Meta:
        verbose_name = '週回顧'
        verbose_name_plural = '週回顧清單'
        unique_together = ('user', 'review_end_date')
        ordering = ['-review_end_date', '-created_at', '-updated_at', '-review_id', '-user_id']
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.review_start_date and self.review_end_date:
            if self.review_start_date >= self.review_end_date:
                raise ValidationError("起始日期必須早於結束日期！")
    
    def __str__(self):
        time_str = self.created_at.strftime('%Y-%m-%d') if self.created_at else "尚未上線"
        return f"報告 ID：{self.review_id}，紀錄區間：{self.review_start_date}～{self.review_end_date}，啟用狀態：{self.is_active}，創建時間：{time_str}"

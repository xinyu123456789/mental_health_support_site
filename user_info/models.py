from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
import uuid

class TopicTag(models.Model):
    '''預設的標籤庫（例如：失眠、焦慮、失戀...）'''
    tag_id = models.BigAutoField(verbose_name = '標籤 ID', primary_key = True)
    name = models.CharField(max_length = 50, unique = True, verbose_name = "標籤名稱")
    category = models.CharField(max_length = 20, choices = [('self', '自我描述'), ('topic', '心理主題')], verbose_name = "標籤分類")

    class Meta:
        verbose_name = '標籤'
        verbose_name_plural = '標籤清單'

    def __str__(self):
        return f"[{self.get_category_display()}] {self.name}"

class User(AbstractUser):
    '''用戶基本資訊（不會給其他用戶看到的）'''
    user_id = models.UUIDField(verbose_name = '用戶 ID', help_text = '不准亂動，會用亂碼產生', editable = False, default = uuid.uuid4, primary_key = True)
    email = models.EmailField(max_length = 500, verbose_name = '用戶 email', help_text = '請輸入電子郵件信箱(ex: 123456789@gmail.com)', unique = True)
    USERNAME_FIELD = 'email' 
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        verbose_name = '用戶'
        verbose_name_plural = '用戶清單'
        ordering = ['-date_joined', '-user_id']
    
    def __str__(self):
        time_str = self.date_joined.strftime('%Y-%m-%d') if self.date_joined else "尚未上線"
        return f"用戶：{self.email} (ID: {self.user_id}) | 加入於：{time_str}"
    
class UserProfile(models.Model):
    '''用戶基本資訊（主要會被別人看到的）'''
    profile_id = models.UUIDField(verbose_name = 'Profile ID', help_text = '不准亂動，會用亂碼產生', editable = False, default = uuid.uuid4, primary_key = True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete = models.CASCADE, verbose_name = '關聯用戶', related_name = 'profile')
    nickname = models.CharField(max_length = 100, verbose_name = '用戶暱稱', help_text = '這就是讓用戶輸入他想要在網站上顯示的暱稱')
    self_description_tags = models.ManyToManyField('TopicTag', verbose_name = '自我描述標籤', blank = True, related_name='profiles_self_tags', limit_choices_to = {'category': 'self'})
    interested_topics = models.ManyToManyField('TopicTag', verbose_name = '有興趣的主題', blank = True, related_name='profiles_topic_tags', limit_choices_to = {'category': 'topic'})
    created_at = models.DateTimeField(auto_now_add = True, verbose_name = 'Profile 創建時間')
    updated_at = models.DateTimeField(auto_now = True, verbose_name = '最後更新時間')
    
    class Meta:
        verbose_name = '用戶資訊'
        verbose_name_plural = '用戶資訊清單'
        ordering = ['-updated_at', 'nickname', '-created_at', '-profile_id']
    
    def __str__(self):
        time_str = self.created_at.strftime('%Y-%m-%d') if self.created_at else "尚未上線"
        return f"ID：{self.profile_id}，檔案: {self.nickname}，創建時間：{time_str}"
    
class SecuritySetting(models.Model):
    '''給用戶設定的安全設定'''
    setting_id = models.UUIDField(verbose_name = '安全設定 ID', help_text = '不准亂動，會用亂碼產生', editable = False, default = uuid.uuid4, primary_key = True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete = models.CASCADE, verbose_name = '關聯用戶', related_name = 'security_settings')
    is_anonymized = models.BooleanField(default = True, db_index = True,  verbose_name = '是否啟用匿名', help_text = '讓用戶選擇是否要匿名發貼文')
    created_at = models.DateTimeField(auto_now_add = True, verbose_name = '安全設定創建時間')
    updated_at = models.DateTimeField(auto_now = True, verbose_name = '最後更新時間')
    
    class Meta:
        verbose_name = '安全設定'
        verbose_name_plural = '安全設定清單'
        ordering = ['-updated_at', '-created_at', '-setting_id']
        
    def __str__(self):
        time_str = self.created_at.strftime('%Y-%m-%d') if self.created_at else "尚未上線"
        return f"安全設定: {self.setting_id}，用戶 ID：{self.user.email}，創建時間：{time_str}"


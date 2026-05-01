from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, UserProfile, SecuritySetting

# 當 User 資料表有存檔動作 (post_save) 時觸發
@receiver(post_save, sender=User)
def create_user_related_models(sender, instance, created, **kwargs):
    # created 是一個布林值，如果是 True 代表這是「第一次被建立」的新帳號
    if created:
        # 自動幫他建立 UserProfile，並把註冊時的 username 先當作暱稱塞進去
        UserProfile.objects.create(
            user=instance, 
            nickname=instance.username
        )
        # 自動建立 SecuritySetting（預設為匿名發文開啟）
        SecuritySetting.objects.create(user=instance)
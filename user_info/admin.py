from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserProfile, SecuritySetting, TopicTag

@admin.register(TopicTag)
class TopicTagAdmin(admin.ModelAdmin):
    list_display = ('tag_id', 'name', 'category')
    list_filter = ('category',)
    search_fields = ('name',)

admin.site.register(User, UserAdmin)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('profile_id', 'user', 'nickname', 'created_at')
    search_fields = ('nickname',)

@admin.register(SecuritySetting)
class SecuritySettingAdmin(admin.ModelAdmin):
    list_display = ('setting_id', 'user', 'is_anonymized')
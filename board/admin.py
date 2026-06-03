from django.contrib import admin
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import Category, Post, Response, OneTimeCode

@admin.action(description='Отправить новостную рассылку выбранным пользователям')
def send_news_newsletter(modeladmin, request, queryset):
    emails = queryset.values_list('email', flat=True)
    send_mail(
        subject='Важные новости нашего игрового сервера!',
        message='Приветствуем! На нашем фанатском сервере вышло крупное обновление. Заходите на сайт доски объявлений!',
        from_email='news@mmoboard.com',
        recipient_list=list(emails),
        fail_silently=False,
    )

admin.site.unregister(User)
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    actions = [send_news_newsletter]

admin.site.register(Category)
admin.site.register(Post)
admin.site.register(Response)
admin.site.register(OneTimeCode)

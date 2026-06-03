from django.db import models
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField

class Category(models.Model):
    # ТЗ: Обязательный фиксированный список категорий
    NAME_CHOICES = [
        ('tank', 'Танки'), ('heal', 'Хилы'), ('dd', 'ДД'),
        ('trader', 'Торговцы'), ('gm', 'Гилдмастеры'), ('quest', 'Квестгиверы'),
        ('smith', 'Кузнецы'), ('leather', 'Кожевники'), ('potion', 'Зельевары'),
        ('spell', 'Мастера заклинаний')
    ]
    name = models.CharField(max_length=20, choices=NAME_CHOICES, unique=True)

    def __str__(self):
        return self.get_name_display()

class OneTimeCode(models.Model):
    # Авторизация по коду: Каждому юзеру — свой временный токен
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otc_codes')
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

class Post(models.Model):
    # ТЗ: Объявления с категориями, автором и RichText (картинки, встроенное видео)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    title = models.CharField(max_length=255)
    text = RichTextField()  # WYSIWYG поле
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Response(models.Model):
    # ТЗ: Простой текстовый отклик к объявлению со статусом принятия
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='responses')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='responses')
    text = models.TextField()
    is_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

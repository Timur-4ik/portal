from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Response
from django.conf import settings


@receiver(post_save, sender=Response)
def send_response_emails(sender, instance, created, **kwargs):
    if created:
        send_mail(
            subject='Новый отклик на ваше объявление',
            message=f'Пользователь {instance.author.username} оставил отклик к вашему объявлению "{instance.post.title}":\n\n{instance.text}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.post.author.email],
        )
    else:
        if instance.is_accepted:
            send_mail(
                subject='Ваш отклик успешно принят!',
                message=f'Автор объявления "{instance.post.title}" принял ваш отклик.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.author.email],
            )

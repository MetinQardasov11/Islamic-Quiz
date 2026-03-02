from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, UserProfile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Yeni kullanıcı oluşturulduğunda otomatik olarak UserProfile oluşturur."""
    if created:
        UserProfile.objects.create(user=instance)

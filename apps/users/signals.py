from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import User


@receiver(pre_save, sender=User)
def delete_old_avatar_on_change(
    sender: type[User], instance: User, **kwargs: object
) -> None:

    if not instance.pk:
        return  # a new user is being created; nothing to compare against
    try:
        old_avatar = User.objects.get(pk=instance.pk).avatar
    except User.DoesNotExist:
        return
    if old_avatar and old_avatar != instance.avatar:
        old_avatar.delete(save=False)

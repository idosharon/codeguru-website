from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.crypto import get_random_string
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.exceptions import ValidationError

# def validate_length(value):
#     return len(value) == 3

INVITE_TIMEOUT = 48
CENTER_CHOICES = [
    ('IND', 'Independent'),
    ('GSA', 'Green Start Academy'),
]

def group_name_validator(name):
    if ' ' in name:
        raise ValidationError("Spaces are not allowed in group name.")
    return name


class CgGroup(models.Model):
    name = models.CharField(max_length=30, unique=True, validators=[group_name_validator])
    # acronym = models.CharField(max_length=3, validators=[validate_length], unique=True)
    owner = models.OneToOneField(User, on_delete=models.CASCADE)
    center = models.CharField(
        max_length=3, choices=CENTER_CHOICES, default="IND")

    def __str__(self):
        return self.name


class Invite(models.Model):
    group = models.OneToOneField(CgGroup, on_delete=models.CASCADE)
    code = models.CharField(max_length=64, unique=True,
                            default=get_random_string(64))
    created = models.DateTimeField(auto_now_add=True)

    def expired(self):
        return timezone.now() > self.created + timedelta(hours=INVITE_TIMEOUT)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    group = models.ForeignKey(CgGroup, null=True, on_delete=models.SET_NULL)
    score = models.IntegerField(default=0)
    picture = models.ImageField(
        upload_to='profile_pics', default='profile_pics/default.jpg')

    def __str__(self):
        return f"Profile of {self.user.username}"


@receiver(post_save, sender=User)
def add_profile(sender, instance, created, **kwargs):
    if created:
        p = Profile(user=instance)
        p.save()

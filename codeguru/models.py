from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.crypto import get_random_string
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

def validate_center(value):
    if len(value) == 3 and value.isalpha() and value.isascii():
        return value
    raise ValidationError("Center should be represented with 3 letters in english.")

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
    name = models.CharField(max_length=30, unique=True,
                            validators=[group_name_validator], verbose_name=_("Name"))
    # acronym = models.CharField(max_length=3, validators=[validate_length], unique=True)
    owner = models.OneToOneField(User, on_delete=models.CASCADE)
    center = models.CharField(
        max_length=3, validators=[validate_center], default="IND", verbose_name=_("Center"))

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        self.center = self.center.upper()
        return super(CgGroup, self).save(*args, **kwargs)


class Invite(models.Model):
    group = models.OneToOneField(CgGroup, on_delete=models.CASCADE)
    code = models.CharField(max_length=64, unique=True,
                            default=get_random_string(64))
    created = models.DateTimeField(auto_now_add=True)

    @property
    def expired(self):
        return timezone.now() > self.created + timedelta(hours=INVITE_TIMEOUT)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    group = models.ForeignKey(CgGroup, null=True, on_delete=models.SET_NULL)
    score = models.IntegerField(default=0)

    def __str__(self):
        return f"Profile of {self.user.username}"


@receiver(post_save, sender=User)
def add_profile(sender, instance, created, **kwargs):
    if created:
        p = Profile(user=instance)
        p.save()

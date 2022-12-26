from __future__ import annotations
from django.utils import timezone
from django.db import models
from django.core.validators import FileExtensionValidator, MinValueValidator
from django.core.exceptions import ValidationError
from codeguru.models import CgGroup
from os.path import join, splitext
from django.utils.crypto import get_random_string
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from uuid import uuid4
from django.db.models.signals import pre_init

warrior_storage = FileSystemStorage(location=settings.PRIVATE_STORAGE_ROOT)


class Challenge(models.Model):
    title = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    required_riddles = models.ManyToManyField("Riddle", symmetrical=False, blank=True)

    class Meta:
        abstract = True

    @property
    def active(self):
        return self.end_date > timezone.now() > self.start_date

    def get_my_model_name(self):
        return self._meta.model_name

    def __str__(self):
        return self.start_date.strftime("%Y-%m-%d")+":"+self.end_date.strftime("%Y-%m-%d")+"_"+self.title

def format_path(instance, file_idx, bin):
    return f"{instance.group.center.ticker}_{instance.group.name}_{file_idx}" + ("" if bin else ".asm")

def war_directory_path(instance, bin):
    if instance.group is None:
        return join("wars", "zombies", str(instance.war.id), uuid4().hex)
    idx = str(instance.warrior_file_idx)
    name = format_path(instance, idx, bin)

    return join("wars", "submissions", str(instance.war.id), "joined_submissions", name)


def riddle_directory_path(instance, filename):
    return join("riddles", str(instance.riddle.id), str(instance.group.id), "solution.zip")
    

def bin_max(value):
    filesize = value.size
    if filesize > 512:
        raise ValidationError("Too large.")
    else:
        return value


def asm_max(value):
    filesize = value.size
    if filesize > 1024**2:
        raise ValidationError("Too large.")
    else:
        return value


def asm_surv_upload(instance, _): return war_directory_path(instance, False)
def bin_surv_upload(instance, _): return war_directory_path(instance, True)

class Riddle(Challenge):
    pass

class War(Challenge):
    amount_of_survivors = models.PositiveIntegerField(
        default=2, validators=[MinValueValidator(1)])
    zombie_mode = models.BooleanField(default=False)
    required_wars = models.ManyToManyField('self', symmetrical=False, blank=True)


class Survivor(models.Model):
    group = models.ForeignKey(
        CgGroup, null=True, editable=False, on_delete=models.CASCADE)
    war = models.ForeignKey(War, null=True, on_delete=models.CASCADE)
    asm_file = models.FileField(null=True, upload_to=asm_surv_upload, validators=[
                                asm_max], storage=warrior_storage)
    bin_file = models.FileField(upload_to=bin_surv_upload, validators=[
                                bin_max], storage=warrior_storage)
    result = models.PositiveIntegerField(default=0)
    upload_date = models.DateTimeField(auto_now_add=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


def warrior_file_idx_modifier(sender, **kwargs):
    if kwargs.get('kwargs').get('warrior_file_idx'):
        sender.warrior_file_idx = kwargs.get('kwargs').pop('warrior_file_idx')


pre_init.connect(warrior_file_idx_modifier, Survivor)

class RiddleSolution(models.Model):
    riddle = models.ForeignKey(Riddle, on_delete=models.CASCADE)
    group = models.ForeignKey(CgGroup, null=True, on_delete=models.CASCADE)
    riddle_solution = models.FileField(
        upload_to=riddle_directory_path, storage=warrior_storage, 
        validators=[FileExtensionValidator(allowed_extensions=['zip'])])
    upload_date = models.DateTimeField(auto_now_add=True)

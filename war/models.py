from django.utils import timezone
from django.db import models
from django.core.validators import FileExtensionValidator, MinValueValidator
from django.core.exceptions import ValidationError
from codeguru.models import CgGroup
from os.path import join, splitext
from django.utils.crypto import get_random_string


class Challenge(models.Model):
    title = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    class Meta:
        abstract = True

    def active(self):
        return self.end_date > timezone.now() > self.start_date

    def get_my_model_name(self):
        return self._meta.model_name

    def __str__(self):
        return self.start_date.strftime("%Y-%m-%d")+":"+self.end_date.strftime("%Y-%m-%d")+"_"+self.title

# TODO: change filename to defined pattern with group name and war

def war_directory_path(instance, filename, file_type):
    if instance.group is None:
        return join("wars", "zombies", instance.war.id, splitext(filename)[0] + "." + file_type)
    return join("wars", "submissions", instance.war.id, instance.group.id, splitext(filename)[0] + "_survivor." + file_type)


def riddle_directory_path(instance, filename):
    return join("riddles", instance.group.id, "solution.zip")


class War(Challenge):
    amount_of_survivors = models.PositiveIntegerField(
        default=2, validators=[MinValueValidator(1)])
    zombie_mode = models.BooleanField(default=False)


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

class Survivor(models.Model):
    group = models.ForeignKey(
        CgGroup, null=True, editable=False, on_delete=models.CASCADE)
    war = models.ForeignKey(War, null=True, on_delete=models.CASCADE)
    asm_file = models.FileField(upload_to=lambda instance, filename: war_directory_path(instance, filename, "asm"), validators=[asm_max])
    bin_file = models.FileField(upload_to=lambda instance, filename: war_directory_path(instance, filename, "dat"), validators=[bin_max])
    result = models.PositiveIntegerField(default=0)

class Riddle(Challenge):
    pass

class RiddleSolution(models.Model):
    riddle = models.ForeignKey(Riddle, on_delete=models.CASCADE)
    group = models.ForeignKey(CgGroup, null=True, on_delete=models.CASCADE)
    riddle_solution = models.FileField(upload_to=riddle_directory_path)
    upload_date = models.DateTimeField(auto_now_add=True)

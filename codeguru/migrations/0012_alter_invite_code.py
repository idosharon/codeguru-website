# Generated by Django 3.2.11 on 2022-01-23 16:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('codeguru', '0011_alter_invite_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invite',
            name='code',
            field=models.CharField(default='oTxVScPQ0WRyecNttXNLhPIljOUmOJSIQjGwfmkzbpJ5N5Gy0NOY1rf59gIjGOXp', max_length=64, unique=True),
        ),
    ]

# Generated by Django 5.1.6 on 2025-05-19 04:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0005_deletedchat'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='is_read',
            field=models.BooleanField(default=False),
        ),
    ]

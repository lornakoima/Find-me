# Generated by Django 4.2.6 on 2024-03-30 16:20

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('Statistics', '0004_alter_case_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='case',
            name='created_at',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]
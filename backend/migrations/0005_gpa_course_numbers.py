# Generated by Django 3.0.6 on 2020-06-10 22:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0004_auto_20200610_2223'),
    ]

    operations = [
        migrations.AddField(
            model_name='gpa',
            name='course_numbers',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]

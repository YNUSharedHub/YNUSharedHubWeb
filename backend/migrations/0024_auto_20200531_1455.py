# Generated by Django 3.0.6 on 2020-05-31 14:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0023_auto_20200531_1452'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course_table',
            name='lessonsAddress',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='course_table',
            name='lessonsName',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='course_table',
            name='lessonsTeacher',
            field=models.CharField(max_length=10, null=True),
        ),
    ]

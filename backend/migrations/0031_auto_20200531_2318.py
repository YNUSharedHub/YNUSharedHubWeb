# Generated by Django 3.0.6 on 2020-05-31 23:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0030_auto_20200531_2317'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='course_code',
            field=models.CharField(max_length=100),
        ),
    ]

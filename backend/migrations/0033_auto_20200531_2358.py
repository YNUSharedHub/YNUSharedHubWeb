# Generated by Django 3.0.6 on 2020-05-31 23:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0032_auto_20200531_2321'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='course_code',
            field=models.CharField(max_length=1000, null=True),
        ),
    ]

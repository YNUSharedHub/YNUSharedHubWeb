# Generated by Django 3.0.6 on 2020-05-31 23:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0029_auto_20200531_2313'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='class_id',
            field=models.PositiveSmallIntegerField(default=1),
        ),
    ]

# Generated by Django 2.0.6 on 2018-06-24 13:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fack', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='topic',
            name='meta_desc',
            field=models.CharField(default='', max_length=512, verbose_name='meta description'),
            preserve_default=False,
        ),
    ]

# Generated by Django 5.0.1 on 2024-06-02 22:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='phone_number',
            field=models.CharField(max_length=15, null=True, verbose_name='Phone number'),
        ),
    ]

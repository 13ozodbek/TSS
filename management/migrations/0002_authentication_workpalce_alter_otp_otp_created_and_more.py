# Generated by Django 5.0.6 on 2024-07-05 15:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='authentication',
            name='workpalce',
            field=models.CharField(default='Apple', max_length=255),
        ),
        migrations.AlterField(
            model_name='otp',
            name='otp_created',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='otp',
            name='otp_type',
            field=models.IntegerField(choices=[(1, 'register'), (2, 'resend'), (3, 'reset')], default=1),
        ),
    ]

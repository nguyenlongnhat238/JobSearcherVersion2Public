# Generated by Django 4.0.3 on 2022-10-03 07:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0004_company_avatar_savedpost_savedpost_unique_user_post'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='apply',
            constraint=models.UniqueConstraint(fields=('user', 'post'), name='unique_user_post_apply'),
        ),
    ]
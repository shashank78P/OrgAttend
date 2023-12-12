# Generated by Django 4.2.5 on 2023-12-10 07:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0011_users_currentactiveorganization'),
    ]

    operations = [
        migrations.AddField(
            model_name='users',
            name='logo',
            field=models.ImageField(default='organization.png', error_messages={'invalid': 'Invalid file (file is not acceptable).'}, max_length=20000, upload_to='organizationLogo'),
        ),
    ]
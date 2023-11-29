# Generated by Django 4.2.5 on 2023-11-26 06:46

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0005_alter_users_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='users',
            name='email',
            field=models.EmailField(db_index=True, error_messages={'invalid': 'Please enter a valid email address.', 'unique': 'User with this email is already exist'}, max_length=254, unique=True, validators=[django.core.validators.EmailValidator()]),
        ),
    ]
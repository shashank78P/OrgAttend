# Generated by Django 4.2.5 on 2023-12-01 14:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0010_alter_users_password'),
    ]

    operations = [
        migrations.AddField(
            model_name='users',
            name='currentActiveOrganization',
            field=models.IntegerField(null=True),
        ),
    ]
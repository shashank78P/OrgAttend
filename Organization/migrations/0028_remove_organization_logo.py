# Generated by Django 4.2.5 on 2023-12-10 03:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Organization', '0027_alter_organization_logo'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='organization',
            name='logo',
        ),
    ]

# Generated by Django 4.2.5 on 2023-12-09 14:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Organization', '0014_leaverequest_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='leaverequest',
            name='fromDate',
            field=models.DateField(max_length=50, null=True),
        ),
    ]

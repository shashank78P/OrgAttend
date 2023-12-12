# Generated by Django 4.2.5 on 2023-12-10 22:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0012_users_logo'),
        ('Organization', '0033_leaverequest_teamid'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('note', models.CharField(max_length=10000, null=True)),
                ('attendance', models.BooleanField(default=False)),
                ('createdAt', models.DateTimeField(auto_now_add=True, null=True)),
                ('updatedAt', models.DateTimeField(auto_now=True, null=True)),
                ('Organization', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='Organization.organization')),
                ('TeamId', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='Organization.team')),
                ('createdBy', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='attendanceTaken', to='Users.users')),
                ('userId', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_employee', to='Users.users')),
            ],
        ),
    ]

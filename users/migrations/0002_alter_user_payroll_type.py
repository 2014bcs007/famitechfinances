# Generated by Django 3.2.9 on 2022-12-08 09:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='payroll_type',
            field=models.CharField(blank=True, choices=[('salary-scale', 'Salary Scale'), ('workback', 'Workback')], default='salary-scale', max_length=255, null=True),
        ),
    ]

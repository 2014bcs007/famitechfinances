# Generated by Django 3.2.9 on 2022-12-06 14:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finances', '0004_auto_20221206_1411'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='date',
            field=models.DateField(blank=True, null=True),
        ),
    ]

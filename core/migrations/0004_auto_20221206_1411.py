# Generated by Django 3.2.9 on 2022-12-06 14:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20221020_1327'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='client',
            name='address',
        ),
        migrations.AddField(
            model_name='client',
            name='address1',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='address2',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='client_contact_reference',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='zipcode',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='config',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='config',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True, verbose_name='last updated on'),
        ),
        migrations.AlterField(
            model_name='template',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='template',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True, verbose_name='last updated on'),
        ),
        migrations.AlterField(
            model_name='term',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='term',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True, verbose_name='last updated on'),
        ),
        migrations.AlterField(
            model_name='termmeta',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='termmeta',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True, verbose_name='last updated on'),
        ),
    ]

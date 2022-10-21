# Generated by Django 3.2.9 on 2022-10-20 12:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_currentuser.db.models.fields
import django_currentuser.middleware


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='termmeta',
            name='created_by',
            field=django_currentuser.db.models.fields.CurrentUserField(default=django_currentuser.middleware.get_current_authenticated_user, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='core_termmeta_created_by', related_query_name='core_termmetas', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='termmeta',
            name='term',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='core.term'),
        ),
        migrations.AddField(
            model_name='termmeta',
            name='updated_by',
            field=django_currentuser.db.models.fields.CurrentUserField(default=django_currentuser.middleware.get_current_authenticated_user, null=True, on_delete=django.db.models.deletion.CASCADE, on_update=True, related_name='core_termmeta_updated_by', related_query_name='core_termmetas', to=settings.AUTH_USER_MODEL, verbose_name='last updated by'),
        ),
        migrations.AddField(
            model_name='term',
            name='created_by',
            field=django_currentuser.db.models.fields.CurrentUserField(default=django_currentuser.middleware.get_current_authenticated_user, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='core_term_created_by', related_query_name='core_terms', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='term',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.term'),
        ),
        migrations.AddField(
            model_name='term',
            name='updated_by',
            field=django_currentuser.db.models.fields.CurrentUserField(default=django_currentuser.middleware.get_current_authenticated_user, null=True, on_delete=django.db.models.deletion.CASCADE, on_update=True, related_name='core_term_updated_by', related_query_name='core_terms', to=settings.AUTH_USER_MODEL, verbose_name='last updated by'),
        ),
        migrations.AddField(
            model_name='template',
            name='created_by',
            field=django_currentuser.db.models.fields.CurrentUserField(default=django_currentuser.middleware.get_current_authenticated_user, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='core_template_created_by', related_query_name='core_templates', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='template',
            name='updated_by',
            field=django_currentuser.db.models.fields.CurrentUserField(default=django_currentuser.middleware.get_current_authenticated_user, null=True, on_delete=django.db.models.deletion.CASCADE, on_update=True, related_name='core_template_updated_by', related_query_name='core_templates', to=settings.AUTH_USER_MODEL, verbose_name='last updated by'),
        ),
        migrations.AddField(
            model_name='log',
            name='content_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='contenttypes.contenttype'),
        ),
        migrations.AddField(
            model_name='log',
            name='user',
            field=django_currentuser.db.models.fields.CurrentUserField(blank=True, default=django_currentuser.middleware.get_current_authenticated_user, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_logs', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='config',
            name='created_by',
            field=django_currentuser.db.models.fields.CurrentUserField(default=django_currentuser.middleware.get_current_authenticated_user, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='core_config_created_by', related_query_name='core_configs', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='config',
            name='updated_by',
            field=django_currentuser.db.models.fields.CurrentUserField(default=django_currentuser.middleware.get_current_authenticated_user, null=True, on_delete=django.db.models.deletion.CASCADE, on_update=True, related_name='core_config_updated_by', related_query_name='core_configs', to=settings.AUTH_USER_MODEL, verbose_name='last updated by'),
        ),
        migrations.AlterUniqueTogether(
            name='term',
            unique_together={('name', 'type', 'is_active')},
        ),
    ]

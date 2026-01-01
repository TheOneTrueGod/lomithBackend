"""
Django project initialization.
Connects automatic database backup signal handler.
"""
from django.apps import AppConfig
from django.core.management.signals import pre_migrate
from .db_backup import pre_migrate_backup

# Connect the backup signal handler
pre_migrate.connect(pre_migrate_backup, dispatch_uid='db_backup_pre_migrate')


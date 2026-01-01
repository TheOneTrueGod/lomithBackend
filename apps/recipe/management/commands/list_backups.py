"""
Management command to list database backups.
"""
from django.core.management.base import BaseCommand
from pathlib import Path
from django.conf import settings
from datetime import datetime


class Command(BaseCommand):
    help = 'List all database backups'

    def add_arguments(self, parser):
        parser.add_argument(
            '--restore',
            type=str,
            help='Restore a specific backup by filename or index',
        )

    def handle(self, *args, **options):
        backup_dir = Path(settings.BASE_DIR) / 'db_backups'
        
        if not backup_dir.exists():
            self.stdout.write(self.style.WARNING('No backup directory found.'))
            return
        
        backups = sorted(backup_dir.glob('db_backup_*.sqlite3'), reverse=True)
        
        if not backups:
            self.stdout.write(self.style.WARNING('No backups found.'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'\nFound {len(backups)} backup(s):\n'))
        
        for i, backup in enumerate(backups, 1):
            size = backup.stat().st_size / 1024  # Size in KB
            try:
                # Extract timestamp from filename
                timestamp_str = backup.stem.replace('db_backup_', '')
                timestamp = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
                formatted_time = timestamp.strftime('%Y-%m-%d %H:%M:%S')
            except:
                formatted_time = 'Unknown'
            
            self.stdout.write(f"  [{i}] {backup.name}")
            self.stdout.write(f"      Date: {formatted_time}")
            self.stdout.write(f"      Size: {size:.2f} KB")
            self.stdout.write(f"      Path: {backup}\n")
        
        # Handle restore if requested
        if options['restore']:
            self.restore_backup(backups, options['restore'])

    def restore_backup(self, backups, restore_arg):
        """Restore a backup by index or filename."""
        try:
            # Try as index first
            index = int(restore_arg) - 1
            if 0 <= index < len(backups):
                backup_path = backups[index]
            else:
                self.stdout.write(self.style.ERROR(f'Invalid backup index: {restore_arg}'))
                return
        except ValueError:
            # Try as filename
            backup_path = None
            for backup in backups:
                if restore_arg in backup.name:
                    backup_path = backup
                    break
            
            if not backup_path:
                self.stdout.write(self.style.ERROR(f'Backup not found: {restore_arg}'))
                return
        
        # Confirm restore
        self.stdout.write(self.style.WARNING(
            f'\n⚠ WARNING: This will replace your current database!'
        ))
        self.stdout.write(f'Restoring from: {backup_path.name}')
        
        import shutil
        
        db_path = Path(settings.DATABASES['default']['NAME'])
        
        # Backup current database before restoring
        if db_path.exists():
            current_backup = Path(settings.BASE_DIR) / 'db_backups' / f'pre_restore_{datetime.now().strftime("%Y%m%d_%H%M%S")}.sqlite3'
            shutil.copy2(db_path, current_backup)
            self.stdout.write(f'Current database backed up to: {current_backup.name}')
        
        # Restore
        shutil.copy2(backup_path, db_path)
        self.stdout.write(self.style.SUCCESS(f'\n✓ Database restored from: {backup_path.name}'))
        self.stdout.write(self.style.SUCCESS('You may need to run migrations if the schema has changed.'))


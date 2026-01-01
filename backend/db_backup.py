"""
Automatic database backup utility for Django migrations.
Backs up the database before migrations run using Django signals.
"""
import shutil
from pathlib import Path
from datetime import datetime
from django.conf import settings


def get_backup_directory():
    """Get or create the backup directory."""
    backup_dir = Path(settings.BASE_DIR) / 'db_backups'
    backup_dir.mkdir(exist_ok=True)
    return backup_dir


def backup_sqlite_database():
    """
    Backup SQLite database before migrations.
    Creates a timestamped copy of the database file.
    """
    db_path = Path(settings.DATABASES['default']['NAME'])
    
    # If database doesn't exist yet (first migration), skip backup
    if not db_path.exists():
        return None
    
    backup_dir = get_backup_directory()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f'db_backup_{timestamp}.sqlite3'
    backup_path = backup_dir / backup_filename
    
    try:
        # Copy the database file
        shutil.copy2(db_path, backup_path)
        print(f"✓ Database backed up to: {backup_path}")
        return str(backup_path)
    except Exception as e:
        print(f"✗ Error backing up database: {e}")
        return None


def backup_database():
    """
    Backup database based on the database engine.
    Currently supports SQLite, can be extended for other databases.
    """
    db_engine = settings.DATABASES['default']['ENGINE']
    
    if 'sqlite' in db_engine:
        return backup_sqlite_database()
    else:
        # For other databases (PostgreSQL, MySQL, etc.), you could use:
        # - pg_dump for PostgreSQL
        # - mysqldump for MySQL
        # - etc.
        print(f"⚠ Automatic backup not implemented for {db_engine}")
        print("  Please backup manually before running migrations")
        return None


# Module-level flag to ensure we only backup once per migration run
_backup_done = False


def pre_migrate_backup(sender, app_config, **kwargs):
    """
    Signal handler that backs up the database before migrations run.
    This is connected to the pre_migrate signal.
    Only backs up once per migration run, not once per app.
    """
    global _backup_done
    
    # Only backup if we're actually running migrations (not just checking)
    import sys
    if 'migrate' in sys.argv and not _backup_done:
        _backup_done = True
        print("\n" + "="*60)
        print("AUTOMATIC DATABASE BACKUP")
        print("="*60)
        backup_path = backup_database()
        if backup_path:
            print(f"Backup location: {backup_path}")
        print("="*60 + "\n")


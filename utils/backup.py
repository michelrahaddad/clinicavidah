import os
import shutil
import sqlite3
import logging
from datetime import datetime
from pathlib import Path

def create_database_backup():
    """Create automatic database backup"""
    try:
        # Get database path
        database_url = os.environ.get("DATABASE_URL", "sqlite:///vidah_medical.db")
        
        if database_url.startswith("sqlite:///"):
            db_path = database_url.replace("sqlite:///", "")
            
            if os.path.exists(db_path):
                # Create backups directory
                backup_dir = Path("backups")
                backup_dir.mkdir(exist_ok=True)
                
                # Create timestamped backup
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_filename = f"vidah_backup_{timestamp}.db"
                backup_path = backup_dir / backup_filename
                
                # Copy database file
                shutil.copy2(db_path, backup_path)
                
                # Keep only last 10 backups
                cleanup_old_backups(backup_dir)
                
                logging.info(f"Database backup created: {backup_path}")
                return str(backup_path)
        
        elif database_url.startswith("postgresql://"):
            # For PostgreSQL, use pg_dump command
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"vidah_backup_{timestamp}.sql"
            backup_dir = Path("backups")
            backup_dir.mkdir(exist_ok=True)
            backup_path = backup_dir / backup_filename
            
            # Extract connection details from URL
            import re
            match = re.match(r'postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)', database_url)
            if match:
                user, password, host, port, dbname = match.groups()
                
                # Set PGPASSWORD environment variable
                env = os.environ.copy()
                env['PGPASSWORD'] = password
                
                # Run pg_dump
                import subprocess
                cmd = [
                    'pg_dump',
                    '-h', host,
                    '-p', port,
                    '-U', user,
                    '-d', dbname,
                    '-f', str(backup_path)
                ]
                
                result = subprocess.run(cmd, env=env, capture_output=True, text=True)
                
                if result.returncode == 0:
                    cleanup_old_backups(backup_dir)
                    logging.info(f"PostgreSQL backup created: {backup_path}")
                    return str(backup_path)
                else:
                    logging.error(f"PostgreSQL backup failed: {result.stderr}")
            
    except Exception as e:
        logging.error(f"Backup creation failed: {e}")
    
    return None

def cleanup_old_backups(backup_dir, keep_count=10):
    """Keep only the most recent backups"""
    try:
        backup_files = list(backup_dir.glob("vidah_backup_*.db")) + list(backup_dir.glob("vidah_backup_*.sql"))
        backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        # Remove old backups
        for old_backup in backup_files[keep_count:]:
            old_backup.unlink()
            logging.info(f"Removed old backup: {old_backup}")
            
    except Exception as e:
        logging.error(f"Backup cleanup failed: {e}")

def schedule_backups():
    """Schedule automatic backups"""
    import threading
    import time
    
    def backup_worker():
        while True:
            try:
                # Create backup every 24 hours
                create_database_backup()
                time.sleep(24 * 60 * 60)  # 24 hours
            except Exception as e:
                logging.error(f"Scheduled backup failed: {e}")
                time.sleep(60 * 60)  # Retry in 1 hour
    
    # Start backup thread
    backup_thread = threading.Thread(target=backup_worker, daemon=True)
    backup_thread.start()
    logging.info("Automatic backup scheduler started")
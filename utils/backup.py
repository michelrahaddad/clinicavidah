import os
import subprocess
import gzip
import shutil
from datetime import datetime, timedelta
from models import BackupConfig
import logging

def create_backup():
    """Create database backup"""
    try:
        # Create backups directory
        backup_dir = 'backups'
        os.makedirs(backup_dir, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'backup_{timestamp}.sql'
        backup_path = os.path.join(backup_dir, backup_filename)
        
        # Get database URL from environment
        db_url = os.environ.get('DATABASE_URL')
        if not db_url:
            raise Exception('DATABASE_URL not found')
        
        # Use pg_dump to create backup
        cmd = f'pg_dump {db_url} > {backup_path}'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise Exception(f'pg_dump failed: {result.stderr}')
        
        # Compress backup
        compressed_path = f'{backup_path}.gz'
        with open(backup_path, 'rb') as f_in:
            with gzip.open(compressed_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        # Remove uncompressed file
        os.remove(backup_path)
        
        # Update backup config
        config = BackupConfig.query.first()
        if config:
            config.ultimo_backup = datetime.utcnow()
            # Calculate next backup
            if config.frequencia == 'daily':
                config.proximo_backup = datetime.utcnow() + timedelta(days=1)
            elif config.frequencia == 'weekly':
                config.proximo_backup = datetime.utcnow() + timedelta(weeks=1)
            elif config.frequencia == 'monthly':
                config.proximo_backup = datetime.utcnow() + timedelta(days=30)
            
            from main import db
            db.session.commit()
        
        logging.info(f'Backup created successfully: {compressed_path}')
        return compressed_path
        
    except Exception as e:
        logging.error(f'Backup creation failed: {e}')
        raise

def restore_backup(backup_path):
    """Restore database from backup"""
    try:
        db_url = os.environ.get('DATABASE_URL')
        if not db_url:
            raise Exception('DATABASE_URL not found')
        
        # Decompress if needed
        if backup_path.endswith('.gz'):
            temp_path = backup_path[:-3]
            with gzip.open(backup_path, 'rb') as f_in:
                with open(temp_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            backup_path = temp_path
        
        # Restore database
        cmd = f'psql {db_url} < {backup_path}'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise Exception(f'psql restore failed: {result.stderr}')
        
        # Clean up temp file if created
        if backup_path.endswith('_temp.sql'):
            os.remove(backup_path)
        
        logging.info(f'Backup restored successfully from: {backup_path}')
        
    except Exception as e:
        logging.error(f'Backup restoration failed: {e}')
        raise

def schedule_backup(config):
    """Schedule automatic backups (placeholder for future cron implementation)"""
    try:
        # This would integrate with a job scheduler like Celery or APScheduler
        # For now, just log the configuration
        logging.info(f'Backup scheduled: {config.frequencia} at {config.horario}')
        
        # Future implementation would set up cron job or scheduled task
        # Example: create_cron_job(config)
        
    except Exception as e:
        logging.error(f'Backup scheduling failed: {e}')

def cleanup_old_backups(retention_days=30):
    """Clean up old backup files"""
    try:
        backup_dir = 'backups'
        if not os.path.exists(backup_dir):
            return
        
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        for filename in os.listdir(backup_dir):
            file_path = os.path.join(backup_dir, filename)
            if os.path.isfile(file_path):
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                if file_time < cutoff_date:
                    os.remove(file_path)
                    logging.info(f'Deleted old backup: {filename}')
        
    except Exception as e:
        logging.error(f'Backup cleanup failed: {e}')
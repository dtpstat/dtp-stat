import os
import shutil
import logging
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from typing import List, Tuple
from django.core.management import call_command
from donations.infrastructure import GoogleDriveUploader, send_telegram_message
from constance import config

logger = logging.getLogger(__name__)


class BackupStorageStrategy(ABC):
    """Abstract base class for backup storage strategies."""
    
    @abstractmethod
    def store_backup(self, backup_filepath, backup_filename):
        """Store the backup using the specific strategy."""
        pass


class LocalBackupStrategy(BackupStorageStrategy):
    """Strategy for storing backups locally."""
    
    def __init__(self, backup_dir='backups'):
        self.backup_dir = backup_dir
        self.latest_dir = os.path.join(backup_dir, 'latest')
        self.weekly_dir = os.path.join(backup_dir, 'weekly')
        
        # Create directories if they don't exist
        os.makedirs(self.latest_dir, exist_ok=True)
        os.makedirs(self.weekly_dir, exist_ok=True)
    
    def store_backup(self, backup_filepath, backup_filename):
        """Store the backup locally in latest and weekly directories."""
        # Copy to latest
        shutil.copy(backup_filepath, os.path.join(self.latest_dir, 'backup.json'))
        
        # Copy to weekly
        shutil.copy(backup_filepath, os.path.join(self.weekly_dir, backup_filename))
        
        # Clean up old weekly backups (older than 7 days)
        self._cleanup_old_backups()
    
    def _cleanup_old_backups(self):
        """Remove weekly backups older than 7 days."""
        seven_days_ago = datetime.now() - timedelta(days=7)
        for filename in os.listdir(self.weekly_dir):
            if filename.startswith('backup-') and filename.endswith('.json'):
                try:
                    backup_date_str = filename.replace('backup-', '').replace('.json', '')
                    backup_date = datetime.strptime(backup_date_str, '%Y-%m-%d')
                    if backup_date < seven_days_ago:
                        os.remove(os.path.join(self.weekly_dir, filename))
                except ValueError:
                    # Ignore files with incorrect date format
                    pass


class GoogleDriveBackupStrategy(BackupStorageStrategy):
    """Strategy for storing backups on Google Drive."""
    
    def __init__(self):
        self.uploader = GoogleDriveUploader()
    
    def store_backup(self, backup_filepath, backup_filename):
        """Store the backup on Google Drive."""
        # Upload the original backup file as the latest backup
        if os.path.exists(backup_filepath):
            # Create a temporary latest backup file for upload
            backup_dir = os.path.dirname(backup_filepath)
            latest_backup_path = os.path.join(backup_dir, 'latest', 'backup.json')
            os.makedirs(os.path.dirname(latest_backup_path), exist_ok=True)
            shutil.copy(backup_filepath, latest_backup_path)
            
            # Upload latest backup
            self.uploader.upload_file(latest_backup_path)
            
            # Upload weekly backup (the original file)
            self.uploader.upload_file(backup_filepath)
            
            # Clean up the temporary latest backup file
            if os.path.exists(latest_backup_path):
                os.remove(latest_backup_path)
        
        # Clean up old weekly backups (older than 7 days)
        self._cleanup_old_backups()
    
    def _cleanup_old_backups(self):
        """Remove weekly backups older than 7 days from Google Drive."""
        try:
            seven_days_ago = datetime.now() - timedelta(days=7)
            
            # Query for files with name starting with 'backup-' and ending with '.json'
            query = "name contains 'backup-' and name contains '.json' and trashed = false"
            results = self.uploader.service.files().list(
                q=query,
                fields="files(id, name, createdTime)"
            ).execute()
            
            files = results.get('files', [])
            
            for file in files:
                try:
                    # Extract date from filename
                    filename = file['name']
                    if filename.startswith('backup-') and filename.endswith('.json'):
                        backup_date_str = filename.replace('backup-', '').replace('.json', '')
                        backup_date = datetime.strptime(backup_date_str, '%Y-%m-%d')
                        
                        # If file is older than 7 days, delete it
                        if backup_date < seven_days_ago:
                            self.uploader.service.files().delete(fileId=file['id']).execute()
                            logger.info(f"Deleted old backup file from Google Drive: {filename}")
                except ValueError:
                    # Ignore files with incorrect date format
                    pass
                except Exception as e:
                    logger.error(f"Error deleting file {file.get('name', 'unknown')}: {e}")
                    
        except Exception as e:
            logger.error(f"Error during Google Drive cleanup: {e}")


class BackupService:
    """Service class for handling database backups with different storage strategies."""
    
    def __init__(self, storage_strategies):
        # type: (List[BackupStorageStrategy]) -> None
        self.storage_strategies = storage_strategies
    
    def create_backup(self):
        """Create a database backup and return the file path and filename."""
        # Define backup directories
        backup_dir = 'backups'
        os.makedirs(backup_dir, exist_ok=True)
        os.makedirs(os.path.join(backup_dir, 'latest'), exist_ok=True)
        
        # Create new backup
        backup_filename = "backup-{}.json".format(datetime.now().strftime('%Y-%m-%d'))
        backup_filepath = os.path.join(backup_dir, backup_filename)
        
        with open(backup_filepath, 'w') as f:
            call_command('dumpdata', 'donations', stdout=f)
        
        return backup_filepath, backup_filename
    
    def store_backup(self, backup_filepath, backup_filename):
        """Store the backup using all configured strategies."""
        for strategy in self.storage_strategies:
            strategy.store_backup(backup_filepath, backup_filename)
        
        # Remove the initial backup file after all strategies have processed it
        if os.path.exists(backup_filepath):
            os.remove(backup_filepath)
    
    def send_notification(self, message):
        """Send a notification via Telegram."""
        chat_id = config.DONATES_REPORT_CHAT_ID
        if chat_id:
            send_telegram_message(chat_id, message)
import logging
from typing import List

from django.core.management.base import BaseCommand
from donations.services.backup_service import (
    BackupService,
    BackupStorageStrategy, LocalBackupStrategy,
    GoogleDriveBackupStrategy,
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Creates a database backup and manages weekly and latest copies.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--upload-to-drive',
            action='store_true',
            help='Upload backup files to Google Drive',
        )

    def handle(self, *args, **options):
        # Initialize backup_service to None
        backup_service = None
        
        try:
            # Determine which strategies to use
            strategies: List[BackupStorageStrategy] = [LocalBackupStrategy()]
            if options['upload_to_drive']:
                strategies.append(GoogleDriveBackupStrategy())
            
            # Create backup service with selected strategies
            backup_service = BackupService(strategies)
            
            # Create and store backup
            backup_filepath, backup_filename = backup_service.create_backup()
            self.stdout.write(self.style.SUCCESS(f'Successfully created backup: {backup_filepath}'))
            
            backup_service.store_backup(backup_filepath, backup_filename)
            self.stdout.write(self.style.SUCCESS('Backup stored successfully'))
            
            # Send success notification
            backup_service.send_notification(f"✅ Backup completed successfully: {backup_filename}")
            
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            self.stdout.write(self.style.ERROR(f'Backup failed: {e}'))
            
            # Send failure notification if backup_service was initialized
            if backup_service:
                backup_service.send_notification(f"❌ Backup failed: {e}")
            raise

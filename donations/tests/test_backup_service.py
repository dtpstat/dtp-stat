import os
import shutil
import unittest
from unittest.mock import patch, MagicMock
from donations.services.backup_service import (
    BackupService, 
    LocalBackupStrategy, 
    GoogleDriveBackupStrategy
)


class TestBackupService(unittest.TestCase):
    
    def setUp(self):
        self.backup_dir = 'test_backups'
        self.latest_dir = os.path.join(self.backup_dir, 'latest')
        self.weekly_dir = os.path.join(self.backup_dir, 'weekly')
        
        # Clean up any existing test directories
        if os.path.exists(self.backup_dir):
            import shutil
            shutil.rmtree(self.backup_dir)
    
    def tearDown(self):
        # Clean up test directories
        if os.path.exists(self.backup_dir):
            import shutil
            shutil.rmtree(self.backup_dir)
    
    @patch('donations.services.backup_service.call_command')
    def test_create_backup(self, mock_call_command):
        # Arrange
        service = BackupService([])
        
        # Act
        backup_filepath, backup_filename = service.create_backup()
        
        # Assert
        self.assertTrue(os.path.exists('backups'))
        self.assertTrue(os.path.exists(os.path.join('backups', 'latest')))
        self.assertTrue(backup_filepath.endswith('.json'))
        self.assertTrue(backup_filename.startswith('backup-'))
        mock_call_command.assert_called_once_with('dumpdata', 'donations', stdout=unittest.mock.ANY)
    
    def test_local_backup_strategy(self):
        # Arrange
        strategy = LocalBackupStrategy(self.backup_dir)
        test_file = os.path.join(self.backup_dir, 'test.json')
        
        # Create a test file
        os.makedirs(self.backup_dir, exist_ok=True)
        with open(test_file, 'w') as f:
            f.write('{"test": "data"}')
        
        # Act
        strategy.store_backup(test_file, 'test.json')
        
        # Assert
        self.assertTrue(os.path.exists(os.path.join(self.latest_dir, 'backup.json')))
        self.assertTrue(os.path.exists(os.path.join(self.weekly_dir, 'test.json')))
        # Original file should be removed by the service, not the strategy
        # self.assertFalse(os.path.exists(test_file))
    
    @patch('donations.services.backup_service.GoogleDriveUploader')
    def test_google_drive_backup_strategy(self, mock_uploader_class):
        # Arrange
        mock_uploader_instance = MagicMock()
        mock_uploader_class.return_value = mock_uploader_instance
        
        strategy = GoogleDriveBackupStrategy()
        
        # Create a test backup file
        backup_dir = 'backups'
        test_file = os.path.join(backup_dir, 'test.json')
        os.makedirs(backup_dir, exist_ok=True)
        with open(test_file, 'w') as f:
            f.write('{"test": "data"}')
        
        # Act
        strategy.store_backup(test_file, 'test.json')
        
        # Assert
        # Check that we uploaded 2 files (latest and weekly)
        self.assertEqual(mock_uploader_instance.upload_file.call_count, 2)
        # Check that the temporary latest file was cleaned up
        self.assertFalse(os.path.exists(os.path.join(backup_dir, 'latest', 'backup.json')))
    
    @patch('donations.services.backup_service.GoogleDriveUploader')
    def test_google_drive_cleanup_old_backups(self, mock_uploader_class):
        # Arrange
        mock_uploader_instance = MagicMock()
        mock_uploader_class.return_value = mock_uploader_instance
        
        # Mock the Google Drive service responses
        mock_files_list = MagicMock()
        mock_files_list.execute.return_value = {
            'files': [
                {'id': 'file1', 'name': 'backup-2023-01-01.json', 'createdTime': '2023-01-01T00:00:00.000Z'},
                {'id': 'file2', 'name': 'backup-2023-01-02.json', 'createdTime': '2023-01-02T00:00:00.000Z'}
            ]
        }
        mock_uploader_instance.service.files().list.return_value = mock_files_list
        mock_uploader_instance.service.files().delete.return_value.execute.return_value = None
        
        strategy = GoogleDriveBackupStrategy()
        
        # Act
        strategy._cleanup_old_backups()
        
        # Assert
        # Check that we listed files
        mock_uploader_instance.service.files().list.assert_called_once()
        # Check that we attempted to delete files
        self.assertEqual(mock_uploader_instance.service.files().delete.call_count, 2)


if __name__ == '__main__':
    unittest.main()
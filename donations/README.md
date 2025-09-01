# Donations App Infrastructure

This document explains how to use the Google Drive Uploader infrastructure component.

## Google Drive Uploader

The `GoogleDriveUploader` class in `donations/infrastructure.py` provides a simple way to upload files to Google Drive.

### Prerequisites

1.  **Enable the Google Drive API:**
    *   Go to the [Google Cloud Console](https://console.cloud.google.com/).
    *   Create a new project or select an existing one.
    *   In the navigation menu, go to **APIs & Services > Library**.
    *   Search for "Google Drive API" and enable it.

2.  **Create OAuth 2.0 Credentials:**
    *   Go to **APIs & Services > Credentials**.
    *   Click **Create Credentials > OAuth client ID**.
    *   Select **Desktop app** as the application type.
    *   Click **Create**.
    *   Click **Download JSON** to download the client secret file.

3.  **Configure Credentials in Django Admin:**
    *   Open the Django admin panel
    *   Navigate to the "Constance Config" section
    *   Find the `DONATES_GOOGLE_CREDENTIALS` field
    *   Paste the content of your downloaded JSON file into this field
    *   Save the configuration

### Usage

1.  **Instantiate the uploader:**

    ```python
    from donations.infrastructure import GoogleDriveUploader

    uploader = GoogleDriveUploader()
    ```

2.  **Upload a file:**

    ```python
    file_id = uploader.upload_file('/path/to/your/file.txt')
    print(f'File uploaded with ID: {file_id}')
    ```

3.  **Upload a file to a specific folder:**

    ```python
    folder_id = 'YOUR_FOLDER_ID'  # Get this from the Google Drive URL
    file_id = uploader.upload_file('/path/to/your/file.txt', folder_id=folder_id)
    print(f'File uploaded with ID: {file_id}')
    ```

### First-time Authorization

The first time you run the code, it will open a browser window and ask you to authorize the application. After you grant permission, the authentication token will be automatically saved to the `DONATES_GOOGLE_TOKEN` field in the Django admin Constance Config. This token will be used for subsequent authentications.

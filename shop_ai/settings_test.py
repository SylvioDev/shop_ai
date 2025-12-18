from .settings import *

# Use an in-memory SQLite database for tests
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

PASSWORD_RESET_TIMEOUT = 2

# Ensure static files are stored locally in tests
STORAGES["staticfiles"] = {
    "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
}

import os

# Disable Cloudinary in the test environment
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

# Disable Cloudinary settings entirely
CLOUDINARY_URL = None
CLOUD_NAME = None
API_KEY = None
API_SECRET = None

# Optional: Disable Cloudinary storage backend if you're using one
CLOUDINARY_STORAGE = None

# Set the MEDIA_URL and MEDIA_ROOT for the test environment
MEDIA_URL = '/media/'  # This can be adjusted based on your app's needs
MEDIA_ROOT = os.path.join(BASE_DIR, 'test_media')  # Save files in 'test_media' directory

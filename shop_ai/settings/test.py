# --- shop_ai/settings_test.py ---
from shop_ai.settings.base import *

# 1. Provide dummy credentials so the library doesn't crash on import
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': 'test_db',
    'API_KEY': 'test_key',
    'API_SECRET': 'test_secret'
}

# 2. Redirect all file saving to local memory (super fast, no files created)
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.InMemoryStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

# 3. Explicitly override the old style storage setting
DEFAULT_FILE_STORAGE = 'django.core.files.storage.InMemoryStorage'

# 4. Remove cloudinary from INSTALLED_APPS for the test process
# This prevents the library from trying to validate credentials
INSTALLED_APPS = [app for app in INSTALLED_APPS if not app.startswith('cloudinary')]

# 5. Use a faster password hasher for tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# 6. Ensure we use an in-memory DB or a specific test DB if not using DATABASE_URL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

DOMAIN_URL = 'http://localhost:8000/'
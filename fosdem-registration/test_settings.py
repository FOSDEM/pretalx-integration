"""
Test settings for fosdem_registration tests.
"""

import os
import sys
from pathlib import Path

# Add pretalx to Python path
pretalx_src_path = "/home/johan/git/fosdem/pretalx/src"
if pretalx_src_path not in sys.path:
    sys.path.insert(0, pretalx_src_path)

# Set environment variables to prevent CONFIG_FILES error
os.environ.setdefault("PRETALX_CONFIG_FILE", "")

# Import base pretalx settings
from pretalx.settings import *  # Import all settings from pretalx

# Override settings for testing
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Email backend for testing
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Static files settings for tests
STATIC_URL = "/static/"
STATIC_ROOT = Path("/tmp/static")

# Disable static files collection and manifest for tests
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

# Disable DEBUG to avoid template rendering issues in tests
DEBUG = False

# Skip staticfiles finders that might cause issues
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "compressor.finders.CompressorFinder",
]

# Make sure fosdem_registration is in INSTALLED_APPS
# Also ensure all required pretalx apps are included for proper migrations
required_apps = ["fosdem_registration"]
for app in required_apps:
    if app not in INSTALLED_APPS:
        INSTALLED_APPS = list(INSTALLED_APPS) + [app]

# Fast password hashers for testing
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",  # Fast for testing
]

# Disable migrations for faster tests (but allow initial sync)
# class DisableMigrations:
#     def __contains__(self, item):
#         return True

#     def __getitem__(self, item):
#         return None

# MIGRATION_MODULES = DisableMigrations()

# Disable caching for tests
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}

# Test-specific logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django.db": {
            "handlers": ["console"],
            "level": "WARNING",  # Reduce DB query noise
        },
    },
}

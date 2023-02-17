from pathlib import Path
from project.settings import BASE_DIR

WWW_FILES_BASE_FOLDER = Path('/www')

FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o777
FILE_UPLOAD_PERMISSIONS = 0o777

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

STATIC_ROOT = WWW_FILES_BASE_FOLDER / 'assets'
STATIC_URL = '/assets/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

MEDIA_URL = '/storage/'
MEDIA_ROOT = WWW_FILES_BASE_FOLDER / 'storage'

FILE_UPLOAD_HANDLERS = [
    'django.core.files.uploadhandler.TemporaryFileUploadHandler',
]


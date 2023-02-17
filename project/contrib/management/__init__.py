import subprocess
from django.conf import settings


def get_git_head_revision():
    try:
        from pygit2 import Repository
        return Repository(settings.BASE_DIR).revparse_single('HEAD^').id
    except ImportError:
        p = subprocess.check_output(['echo `git log --short --pretty=oneline --abbrev=commit -1`'], shell=True)
        return str(p)[2:-3]


def get_git_head_revision_short():
    p = subprocess.check_output(['git rev-parse --short HEAD'], shell=True)
    return str(p)[2:-3]

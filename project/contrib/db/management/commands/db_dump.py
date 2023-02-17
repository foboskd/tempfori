# coding: utf-8
import os
import subprocess
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--file-name', dest='file_name', type=str, default=None)
        parser.add_argument('--router', dest='router', action='store', default='default')

    def handle(self, *args, **options):
        dbs = settings.DATABASES[options.get('router')]
        file_name = options.get('file_name') or '%s.sql' % dbs['NAME']
        file_path = os.path.abspath(file_name).replace('.tar.gz', '')
        cmd = '''
export PGPASSWORD={3};
{0} {4} \\
    --port={5} \\
    --username={2} \\
    --dbname={1} \\
    --format=p \\
    --verbose \\
    --clean \\
    --no-owner \\
    --no-privileges \\
    --file={6}'''.format(
            dbs.get('PGDUMP', 'pg_dump'),
            dbs.get('NAME'),
            dbs.get('USER'),
            dbs.get('PASSWORD'),
            ('--host=%s' % dbs.get('HOST')) if dbs.get('HOST') else '',
            dbs.get('PORT'),
            file_path
        )
        proc = subprocess.Popen(cmd, shell=True)
        proc.wait()
        cmd = '''cd {0}; xz -vfz {1}'''.format(
            os.path.dirname(file_path),
            os.path.basename(file_path)
        )
        proc = subprocess.Popen(cmd, shell=True)
        proc.wait()

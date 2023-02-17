from cacheops import invalidate_all
from django.core.management.base import BaseCommand
from django.db import connection

from d11.tasks import d11_mviews_rebuild

SQL = '''
UPDATE d11_doc
SET
    last_date_abis_manual_changes = _.max_cards_updated_at
FROM
    (
        SELECT
            d.id,
            MAX(C.updated_at) AS max_cards_updated_at
        FROM
            d11_doc               AS d
            JOIN d11_docalephcard AS C ON TRUE
                AND d.id = C.doc_id

        WHERE
            TRUE
            AND d.last_date_abis_manual_changes IS NULL
        GROUP BY
            d.id
    ) AS _
WHERE
    TRUE
    AND d11_doc.id = _.id
'''


class Command(BaseCommand):
    def handle(self, *args, **options):
        cursor = connection.cursor()
        cursor.execute(SQL)
        invalidate_all()
        d11_mviews_rebuild()

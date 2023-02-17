import shutil
from pathlib import Path
from django.db import migrations


def f(*x):
    from d11.models import DocFileValue, DocFieldValue, DocFieldType

    for v in DocFieldValue.objects.filter(field__type=DocFieldType.FILE):
        doc_file_value = DocFileValue(
            doc=v.doc,
            created_at=v.created_at,
            updated_at=v.updated_at,
            field=v.field
        )
        doc_file_value.value = DocFileValue._meta.get_field('value').generate_filename(doc_file_value, v.python_value)
        doc_file_value_path = Path(doc_file_value.value.path)
        doc_file_value_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            shutil.move(v.python_value, str(doc_file_value_path))
            doc_file_value.save()
        except FileNotFoundError:
            pass
        v.delete()


class Migration(migrations.Migration):
    dependencies = [
        ('d11', '0014_docs_files'),
    ]

    operations = [
        migrations.RunPython(f, lambda *x: None)
    ]

import os

# 10.251.246.104 тест
# 10.251.250.104 прод
ALEPH_HOST = os.environ.get('ALEPH_HOST') or '10.251.246.104'
ALEPH_USER = os.environ.get('ALEPH_USER') or 'm505'
ALEPH_PASSWORD = os.environ.get('ALEPH_PASSWORD') or 'Zz123456'

ALEPH_UPLOAD_DIR = os.environ.get('ALEPH_UPLOAD_DIR') or '/exlibris/u50_5/rsl01/source/D11-upload'

ALEPH_EXPORT_BOTH_CARDS_CREATE_COMMAND = (
        os.environ.get('ALEPH_EXPORT_BOTH_CARDS_CREATE_COMMAND')
        or '/exlibris/u50_5/rsl01/conv/diss/r1_diss_new'
)
ALEPH_EXPORT_SINGLE_CARD_CREATE_COMMAND = (
        os.environ.get('ALEPH_EXPORT_SINGLE_CARD_CREATE_COMMAND')
        or '/exlibris/u50_5/rsl01/conv/diss/r1b_diss_new'
)
ALEPH_EXPORT_CREATE_RESULT_DIR = (
        os.environ.get('ALEPH_EXPORT_CREATE_RESULT_DIR')
        or '/exlibris/u50_5/rsl01/source/diss_r1'
)

ALEPH_EXPORT_UPDATE_COMMAND = (
        os.environ.get('ALEPH_EXPORT_UPDATE_COMMAND')
        or '/exlibris/u50_5/rsl01/conv/diss/r3_diss_update'
)
ALEPH_EXPORT_UPDATE_RESULT_DIR = (
        os.environ.get('ALEPH_EXPORT_UPDATE_RESULT_DIR')
        or '/exlibris/u50_5/rsl01/source/diss_r3'
)

ALEPH_IMPORT_ALEPH_ID_SUFFIX = os.environ.get('ALEPH_IMPORT_ALEPH_ID_SUFFIX') or 'RSL01'
ALEPH_IMPORT_COMMAND = (
        os.environ.get('ALEPH_IMPORT_COMMAND')
        or '/exlibris/u50_5/rsl01/conv/diss/r2_diss_unload'
)
ALEPH_IMPORT_RESULT_DIR = (
        os.environ.get('ALEPH_IMPORT_RESULT_DIR')
        or '/exlibris/u50_5/rsl01/source/diss_r2'
)

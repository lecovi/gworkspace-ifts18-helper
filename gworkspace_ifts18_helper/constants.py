"""
Constants used in gworkspace-ifts18-helper.
"""

SERVICE_ACCOUNT_FILE = 'credentials/credentials3.json'
SCOPES = [
    'https://www.googleapis.com/auth/admin.directory.user',
    'https://www.googleapis.com/auth/gmail.compose', 
]
GWORKSPACE_OWNER = 'colomboleandro@ifts18.edu.ar'

STUDENTS_DATA_FILE = "assets/2022-pp3-alumnos.csv"
NO_REPLY_EMAIL = 'no-reply@ifts18.edu.ar'
INSCRIPTIONS_EMAIL = 'inscripciones@ifts18.edu.ar'
INSCRIPTIONS_EMAIL_HEADER = f'Inscripciones IFTS18 <{INSCRIPTIONS_EMAIL}>'

MAIN_DOMAIN = 'ifts18.edu.ar'
STUDENTS_DOMAIN = 'ifts18.edu.ar'
STUDENTS_ORGUNIT_PATH = "/Alumnos"

DEFAULT_PASSWORD_LENGTH = 16
DEFAULT_PASSWORD_NUMBER_DIGITS = 5

ACCOUNTS_LOGFILE = "accounts.json"
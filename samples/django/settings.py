# Django settings for gcheky_django project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Gchecky Demo', 'gchecky@gmail.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = ''           # 'postgresql', 'mysql', 'sqlite3' or 'ado_mssql'.
DATABASE_NAME = ''             # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. All choices can be found here:
# http://www.postgresql.org/docs/current/static/datetime-keywords.html#DATETIME-TIMEZONE-SET-TABLE
TIME_ZONE = 'Europe/Paris'

# Language code for this installation. All choices can be found here:
# http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
# http://blogs.law.harvard.edu/tech/stories/storyReader$15
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# path to the root directory of the project. Something like:
SITE_ROOT = '/var/www/gchecky_django'

# Absolute path to the directory that holds media.
MEDIA_ROOT = '%s/pictures' % (SITE_ROOT,)

# URL that handles the media served from MEDIA_ROOT.
MEDIA_URL = 'http://media.gchecky.com'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
ADMIN_MEDIA_PREFIX = '%s/admin/' % (MEDIA_URL,)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'nyn9=sqwertymyht0j3p7ki0b3!98+p(vz$$e5d67yte$)j%%52'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
)
ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    SITE_ROOT + '/template',
    # Put strings here, like "/home/html/django_templates".
    # Always use forward slashes, even on Windows.
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.markup',

    'gchecky_common',
    'gchecky_digital',
    'gchecky_donation',
)

# Google checkout information
# Gchecky demo sandbox account info:
gcheckout_vendor_id = '618492934414682'
gcheckout_merchant_key = 't2mBWWytbm_JlIiLzaemoQ'
gcheckout_is_sandbox = True # True for testing, False for production
gcheckout_currency = 'GBP' # 'USD' or 'GBP'

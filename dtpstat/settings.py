import os
import environ

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, '.env')

env = environ.Env()
if os.path.exists(ENV_PATH):
    env.read_env(ENV_PATH)

# APP SETTINGS FROM ENV
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])
DEBUG = env.bool('DEBUG', default=False)
NEXTJS_BASE_URL = env('NEXTJS_BASE_URL', default='https://dtp-stat-on-nextjs.netlify.app')
NEXTJS_IFRAME_WITH_COMMENTS = env('NEXTJS_IFRAME_WITH_COMMENTS', default=False)
NEXTJS_IFRAME_WITH_MAP = env('NEXTJS_IFRAME_WITH_MAP', default=False)
SECRET_KEY = env('SECRET_KEY')
YANDEX_TOKEN = env('YANDEX_TOKEN')
HERE_TOKEN = env('HERE_TOKEN')
PRODUCTION_HOST = env('PRODUCTION_HOST', default='dtp-stat.ru')
PROXY_LIST = env('PROXY_LIST', default=[])


# Django stuff
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.gis',
    'django.contrib.sitemaps',
    'data',
    'application',
    'rest_framework',
    'django_filters',
    'ckeditor',
    'ckeditor_uploader',
    'captcha',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'corsheaders',
    'application.templatetags.tags',
    'constance',
    'constance.backends.database',
    'django_q',
    'django_cryptography',
    'publisher',
]

SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware'
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'publisher.middleware.TimezoneMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

if DEBUG:
    CORS_ORIGIN_ALLOW_ALL = True
else:
    CORS_ORIGIN_ALLOW_ALL = False
    CORS_ALLOWED_ORIGINS = env.list(
        'CORS_ALLOWED_ORIGINS',
        default=[f'https://{PRODUCTION_HOST}']
    )

ROOT_URLCONF = 'dtpstat.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.i18n',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'application.context_processors.get_donate_data',
                'application.context_processors.settings',
                'constance.context_processors.config',
            ],
        },
    },
]

WSGI_APPLICATION = 'dtpstat.wsgi.application'

FIRST_DAY_OF_WEEK=1

DATABASES = {
    'default': env.db(),
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',),
    'DEFAULT_PAGINATION_CLASS': None,
}
LANGUAGE_CODE = 'ru'
USE_TZ = True
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = False

# Supported languages
from django.utils.translation import gettext_lazy as _
LANGUAGES = [
    ('ru', _('Russian')),
    ('en', _('English')),
]

# Path for translation files
LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]

# Language cookie settings
LANGUAGE_COOKIE_NAME = 'django_language'
LANGUAGE_COOKIE_AGE = 31536000  # 1 year
LANGUAGE_COOKIE_PATH = '/'
LANGUAGE_COOKIE_DOMAIN = None
LANGUAGE_COOKIE_SECURE = False if DEBUG else True
LANGUAGE_COOKIE_HTTPONLY = False
LANGUAGE_COOKIE_SAMESITE = 'Lax' if DEBUG else 'None'
DATETIME_FORMAT = 'd.m.Y H:i'
DATE_FORMAT = 'd.m.Y'

CKEDITOR_UPLOAD_PATH = 'uploads/'
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'UltraFull',
        'height': 300,
        'toolbar_UltraFull': [
            ['Font', 'FontSize', 'Format'],
            ['Bold', 'Italic', 'Underline', 'Strike', 'Subscript', 'Superscript', '-', 'RemoveFormat'],
            [
                'NumberedList', 'BulletedList', '-',
                'Outdent', 'Indent', '-',
                'Blockquote', '-',
                'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'
            ],
            ['Link', 'Unlink', 'Anchor'],
            ['Image', 'Flash', 'Table', 'HorizontalRule', 'PageBreak', 'Smiley', 'SpecialChar'],
            ['Cut', 'Copy', 'Paste', 'PasteText', 'PasteFromWord', '-', 'Undo', 'Redo'],
            ['TextColor', 'BGColor'],
            ['Maximize', 'Source'],
        ],
        'language': 'ru',
    },
    'social_networks': {
        'toolbar': [],
        'autoGrow_minHeight': 250,
        'autoGrow_maxHeight': 600,
        'autoGrow_onStartup': True,
        'toolbarCanCollapse': True,
        'language': 'ru',
        'removeFormatTags': (
            'b,i,u,strike,strong,em,hr,a,img,blockquote'
        ),
    },
}

STATIC_URL = '/static/'
STATIC_ROOT = env('STATIC_ROOT')
if env('STATICFILES_DIRS'):
    STATICFILES_DIRS = [env('STATICFILES_DIRS')]

MEDIA_URL = '/media/'
MEDIA_ROOT = env('MEDIA_ROOT', default=os.path.join(BASE_DIR, 'media'))

DECIMAL_SEPARATOR="."

SILENCED_SYSTEM_CHECKS = ['captcha.recaptcha_test_key_error']

RECAPTCHA_PUBLIC_KEY = env('RECAPTCHA_PUBLIC_KEY')
RECAPTCHA_PRIVATE_KEY = env('RECAPTCHA_PRIVATE_KEY')

LOGIN_REDIRECT_URL = '/board/'
ACCOUNT_FORMS = {'signup': 'application.forms.MyCustomSignupForm'}
ACCOUNT_AUTHENTICATED_LOGIN_REDIRECTS = True
ACCOUNT_USER_MODEL_EMAIL_FIELD = None
ACCOUNT_EMAIL_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'username'

if not DEBUG:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
            'LOCATION': 'default_cache',
        }
    }
else:
    pass

CONSTANCE_BACKEND = 'constance.backends.database.DatabaseBackend'

CONSTANCE_CONFIG = {
    'DONATE_SUM_TOTAL': (0, 'Сумма донатов'),
    'DONATE_SUM_GOAL': (100000, 'Цель сбора'),
    'DONATE_END_DATE': ('2025-12-31', 'Дата окончания сбора'),
    'SHOW_LANGUAGE_SWITCHER': (False, 'Показывать переключатель языков'),
}

Q_CLUSTER = {
    'name': env('Q_CLUSTER_NAME', default='DjangoORM'),             # имя кластера
    'workers': env.int('Q_CLUSTER_WORKERS', default=2),             # количество воркеров
    'recycle': env.int('Q_CLUSTER_RECYCLE', default=500),           # перезапуск воркеров после N задач
    'timeout': env.int('Q_CLUSTER_TIMEOUT', default=120),           # таймаут выполнения задачи
    'retry': env.int('Q_CLUSTER_RETRY', default=180),               # время ожидания перед повтором задачи
    'save_limit': env.int('Q_CLUSTER_SAVE_LIMIT', default=250),     # максимальное количество сохранённых задач
    'queue_limit': env.int('Q_CLUSTER_QUEUE_LIMIT', default=100),   # максимальный размер очереди
    'orm': 'default',                                               # используем базу данных Django 
}

DJANGO_CRYPTOGRAPHY_KEY = env('DJANGO_ENCRYPTION_KEY')

if not DJANGO_CRYPTOGRAPHY_KEY:
    from django.core.exceptions import ImproperlyConfigured
    raise ImproperlyConfigured(
        "DJANGO_CRYPTOGRAPHY_KEY must be set in the environment"
    )
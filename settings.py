INSTALLED_APPS = [
    # other apps...
    'django_crontab',
    # other apps...
]

CRONJOBS = [
    ('0 0 * * *', 'django.core.management.call_command', ['delete_expired_accounts']),
] 
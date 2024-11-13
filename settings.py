INSTALLED_APPS = [
    ...
    'django_crontab',
    ...
]

CRONJOBS = [
    ('0 0 * * *', 'django.core.management.call_command', ['delete_expired_accounts']),
] 
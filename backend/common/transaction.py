from django.conf import settings
from django.db import transaction

__all__ = ('on_commit',)


def on_commit(fn, *args, **kwargs):
    if transaction.get_autocommit() or getattr(settings, 'CELERY_ALWAYS_EAGER', False):
        fn(*args, **kwargs)
    else:
        transaction.on_commit(lambda: fn(*args, **kwargs))
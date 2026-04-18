"""
chat/management/commands/purge_old_messages.py
===============================================
Permanently deletes chat messages older than CHAT_MESSAGE_EXPIRY_DAYS.

Usage (manual):
    python manage.py purge_old_messages

Usage (automated via cron):
    # Run daily at 3 AM
    0 3 * * * /srv/wanderly/venv/bin/python /srv/wanderly/manage.py purge_old_messages >> /var/log/wanderly/purge.log 2>&1

Usage (automated via Celery Beat):
    In your celery config:
        from celery.schedules import crontab
        CELERY_BEAT_SCHEDULE = {
            'purge-old-messages': {
                'task': 'chat.tasks.purge_old_messages',
                'schedule': crontab(hour=3, minute=0),
            },
        }

Why this matters (GDPR / Privacy):
    Retaining personal communication data indefinitely creates legal risk.
    Deleting messages after 180 days limits exposure in the event of a breach
    and satisfies data-minimisation requirements under the GDPR.
"""

from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = 'Permanently delete chat messages older than CHAT_MESSAGE_EXPIRY_DAYS days.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show how many messages would be deleted without actually deleting them.',
        )

    def handle(self, *args, **options):
        # Import here to avoid issues if the app is not fully loaded.
        from chat.models import Message

        expiry_days = getattr(settings, 'CHAT_MESSAGE_EXPIRY_DAYS', 180)
        cutoff = timezone.now() - timedelta(days=expiry_days)

        expired_qs = Message.objects.filter(created_at__lt=cutoff)
        count = expired_qs.count()

        if options['dry_run']:
            self.stdout.write(
                self.style.WARNING(
                    f'[DRY RUN] Would delete {count} messages older than {expiry_days} days.'
                )
            )
            return

        if count == 0:
            self.stdout.write(self.style.SUCCESS('No expired messages to delete.'))
            return

        # Use delete() directly on the queryset for efficiency.
        # Django's ORM issues a single DELETE SQL statement instead of
        # iterating over Python objects, which is critical for large datasets.
        deleted, _ = expired_qs.delete()

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully deleted {deleted} messages older than {expiry_days} days '
                f'(cutoff: {cutoff.strftime("%Y-%m-%d %H:%M UTC")}).'
            )
        )

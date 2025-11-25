from django.core.management.base import BaseCommand
from django.utils import timezone

from mailings.models import Mailing
from mailings.services import MailingSender


class Command(BaseCommand):
    help = 'Отправляет запланированные рассылки'

    def handle(self, *args, **options):
        now = timezone.now()
        mailings = Mailing.objects.filter(
            is_active=True,
            start_at__lte=now,
            finish_at__gte=now,
            status__in=[Mailing.Status.CREATED, Mailing.Status.RUNNING],
        )
        if not mailings.exists():
            self.stdout.write('Подходящих рассылок нет.')
            return

        for mailing in mailings:
            sender = MailingSender(mailing)
            attempts = sender.send()
            self.stdout.write(f'Рассылка #{mailing.pk}: отправлено {attempts} писем.')



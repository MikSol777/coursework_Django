from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from .models import Mailing, MailingAttempt


class MailingSender:
    def __init__(self, mailing: Mailing):
        self.mailing = mailing

    def send(self):
        if not self.mailing.is_active:
            return 0

        now = timezone.now()
        attempts = 0
        for client in self.mailing.clients.all():
            attempts += 1
            try:
                send_mail(
                    subject=self.mailing.message.subject,
                    message=self.mailing.message.body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[client.email],
                    fail_silently=False,
                )
                status = MailingAttempt.AttemptStatus.SUCCESS
                response = 'Отправлено'
            except Exception as exc:
                status = MailingAttempt.AttemptStatus.FAIL
                response = str(exc)

            MailingAttempt.objects.create(
                mailing=self.mailing,
                client=client,
                status=status,
                server_response=response,
            )

        self.mailing.last_launch_at = now
        if now >= self.mailing.finish_at:
            self.mailing.status = Mailing.Status.COMPLETED
        else:
            self.mailing.status = Mailing.Status.RUNNING
        self.mailing.save(update_fields=['last_launch_at', 'status'])
        return attempts



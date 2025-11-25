from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Client(models.Model):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    comment = models.TextField(blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='clients')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('full_name',)
        verbose_name = 'Получатель'
        verbose_name_plural = 'Получатели'
        permissions = [
            ('view_all_clients', 'Может просматривать всех получателей'),
        ]

    def __str__(self):
        return f'{self.full_name} ({self.email})'


class Message(models.Model):
    subject = models.CharField(max_length=255)
    body = models.TextField()
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='messages')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        permissions = [
            ('view_all_messages', 'Может просматривать все сообщения'),
        ]

    def __str__(self):
        return self.subject


class Mailing(models.Model):
    class Status(models.TextChoices):
        CREATED = 'Создана', 'Создана'
        RUNNING = 'Запущена', 'Запущена'
        COMPLETED = 'Завершена', 'Завершена'

    start_at = models.DateTimeField()
    finish_at = models.DateTimeField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.CREATED)
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='mailings')
    clients = models.ManyToManyField(Client, related_name='mailings')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mailings')
    last_launch_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'
        permissions = [
            ('view_all_mailings', 'Может просматривать все рассылки'),
        ]

    def __str__(self):
        return f'Рассылка #{self.pk}'

    def clean(self):
        if self.finish_at <= self.start_at:
            raise ValidationError('Дата окончания должна быть позже даты начала.')

    @property
    def is_running(self):
        return self.status == self.Status.RUNNING

    @property
    def is_completed(self):
        return self.status == self.Status.COMPLETED

    @property
    def recipients_count(self):
        return self.clients.count()

    def update_status(self):
        now = timezone.now()
        if now >= self.finish_at:
            self.status = self.Status.COMPLETED
        elif now >= self.start_at:
            self.status = self.Status.RUNNING
        else:
            self.status = self.Status.CREATED
        self.save(update_fields=['status'])


class MailingAttempt(models.Model):
    class AttemptStatus(models.TextChoices):
        SUCCESS = 'Успешно', 'Успешно'
        FAIL = 'Не успешно', 'Не успешно'

    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE, related_name='attempts')
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True, related_name='attempts')
    attempted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=AttemptStatus.choices)
    server_response = models.TextField()

    class Meta:
        ordering = ('-attempted_at',)
        verbose_name = 'Попытка рассылки'
        verbose_name_plural = 'Попытки рассылок'

    def __str__(self):
        client_email = self.client.email if self.client else 'неизвестно'
        return f'Попытка #{self.pk} для {client_email}'


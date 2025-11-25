from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


def send_activation_email(user, request):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    activation_url = request.build_absolute_uri(reverse('users:activate', args=[uid, token]))
    subject = 'Подтверждение регистрации'
    message = (
        f'Здравствуйте, {user.get_full_name() or user.email}!\n\n'
        f'Для подтверждения регистрации перейдите по ссылке: {activation_url}\n\n'
        'Если вы не регистрировались на сайте, просто проигнорируйте это письмо.'
    )
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])



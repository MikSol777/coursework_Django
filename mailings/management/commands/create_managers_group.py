from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Создает группу «Менеджеры» и назначает необходимые права'

    def handle(self, *args, **options):
        group, _ = Group.objects.get_or_create(name='Менеджеры')
        required_perms = [
            'view_all_clients',
            'view_all_messages',
            'view_all_mailings',
        ]
        permissions = Permission.objects.filter(codename__in=required_perms)
        group.permissions.set(permissions)
        self.stdout.write('Группа «Менеджеры» обновлена.')



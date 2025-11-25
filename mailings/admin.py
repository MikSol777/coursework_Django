from django.contrib import admin

from .models import Client, Mailing, MailingAttempt, Message


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('email', 'full_name', 'owner', 'created_at')
    search_fields = ('email', 'full_name')
    list_filter = ('owner',)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'owner', 'created_at')
    search_fields = ('subject',)
    list_filter = ('owner',)


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ('id', 'start_at', 'finish_at', 'status', 'owner', 'is_active')
    list_filter = ('status', 'owner', 'is_active')
    search_fields = ('message__subject',)
    filter_horizontal = ('clients',)


@admin.register(MailingAttempt)
class MailingAttemptAdmin(admin.ModelAdmin):
    list_display = ('mailing', 'client', 'status', 'attempted_at')
    list_filter = ('status', 'attempted_at')
    search_fields = ('client__email',)

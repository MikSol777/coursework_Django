from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control, cache_page
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
    View,
)

from .forms import ClientForm, MailingForm, MessageForm
from .mixins import OwnerFormMixin, OwnerQuerysetMixin
from .models import Client, Mailing, MailingAttempt, Message
from .services import MailingSender
from .utils import user_is_manager


CACHE_TTL = settings.CACHES['default'].get('TIMEOUT', 300)


@method_decorator(cache_page(CACHE_TTL), name='dispatch')
@method_decorator(cache_control(public=True, max_age=60), name='dispatch')
class DashboardView(TemplateView):
    template_name = 'mailings/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mailing_total'] = Mailing.objects.count()
        context['mailing_active'] = Mailing.objects.filter(status=Mailing.Status.RUNNING).count()
        context['unique_clients'] = Client.objects.values('email').distinct().count()
        return context


class ClientListView(OwnerQuerysetMixin, ListView):
    model = Client
    template_name = 'mailings/client_list.html'
    context_object_name = 'clients'
    allow_manager_view_all = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_manager'] = user_is_manager(self.request.user)
        return context


class ClientDetailView(OwnerQuerysetMixin, DetailView):
    model = Client
    template_name = 'mailings/client_detail.html'
    context_object_name = 'client'
    allow_manager_view_all = True


class ClientCreateView(OwnerFormMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = 'mailings/client_form.html'
    success_url = reverse_lazy('mailings:clients')

    def form_valid(self, form):
        messages.success(self.request, 'Получатель успешно создан.')
        return super().form_valid(form)


class ClientUpdateView(OwnerQuerysetMixin, OwnerFormMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = 'mailings/client_form.html'
    success_url = reverse_lazy('mailings:clients')

    def form_valid(self, form):
        messages.success(self.request, 'Получатель обновлен.')
        return super().form_valid(form)


class ClientDeleteView(OwnerQuerysetMixin, DeleteView):
    model = Client
    template_name = 'mailings/confirm_delete.html'
    success_url = reverse_lazy('mailings:clients')
    context_object_name = 'object'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Получатель удален.')
        return super().delete(request, *args, **kwargs)


class MessageListView(OwnerQuerysetMixin, ListView):
    model = Message
    template_name = 'mailings/message_list.html'
    context_object_name = 'messages'
    allow_manager_view_all = True


class MessageDetailView(OwnerQuerysetMixin, DetailView):
    model = Message
    template_name = 'mailings/message_detail.html'
    context_object_name = 'message'
    allow_manager_view_all = True


class MessageCreateView(OwnerFormMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailings/message_form.html'
    success_url = reverse_lazy('mailings:messages')

    def form_valid(self, form):
        messages.success(self.request, 'Сообщение сохранено.')
        return super().form_valid(form)


class MessageUpdateView(OwnerQuerysetMixin, OwnerFormMixin, UpdateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailings/message_form.html'
    success_url = reverse_lazy('mailings:messages')

    def form_valid(self, form):
        messages.success(self.request, 'Сообщение обновлено.')
        return super().form_valid(form)


class MessageDeleteView(OwnerQuerysetMixin, DeleteView):
    model = Message
    template_name = 'mailings/confirm_delete.html'
    success_url = reverse_lazy('mailings:messages')
    context_object_name = 'object'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Сообщение удалено.')
        return super().delete(request, *args, **kwargs)


class MailingListView(OwnerQuerysetMixin, ListView):
    model = Mailing
    template_name = 'mailings/mailing_list.html'
    context_object_name = 'mailings'
    allow_manager_view_all = True


class MailingDetailView(OwnerQuerysetMixin, DetailView):
    model = Mailing
    template_name = 'mailings/mailing_detail.html'
    context_object_name = 'mailing'
    allow_manager_view_all = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['attempts'] = self.object.attempts.select_related('client')[:10]
        context['is_manager'] = user_is_manager(self.request.user)
        return context


class MailingCreateView(OwnerFormMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailings/mailing_form.html'
    success_url = reverse_lazy('mailings:mailing_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Рассылка создана.')
        return super().form_valid(form)


class MailingUpdateView(OwnerQuerysetMixin, OwnerFormMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailings/mailing_form.html'
    success_url = reverse_lazy('mailings:mailing_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Рассылка обновлена.')
        return super().form_valid(form)


class MailingDeleteView(OwnerQuerysetMixin, DeleteView):
    model = Mailing
    template_name = 'mailings/confirm_delete.html'
    success_url = reverse_lazy('mailings:mailing_list')
    context_object_name = 'object'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Рассылка удалена.')
        return super().delete(request, *args, **kwargs)


class MailingSendView(LoginRequiredMixin, View):
    def post(self, request, pk):
        mailing = get_object_or_404(Mailing, pk=pk)
        if mailing.owner != request.user:
            messages.error(request, 'Вы можете отправлять только свои рассылки.')
            return redirect('mailings:mailing_detail', pk=pk)
        sender = MailingSender(mailing)
        attempts = sender.send()
        if attempts:
            messages.success(request, f'Рассылка отправлена ({attempts} писем).')
        else:
            messages.info(request, 'Нет активных получателей или рассылка отключена.')
        return redirect('mailings:mailing_detail', pk=pk)


class MailingToggleActiveView(LoginRequiredMixin, View):
    def post(self, request, pk):
        if not user_is_manager(request.user):
            messages.error(request, 'Недостаточно прав для отключения рассылки.')
            return redirect('mailings:mailing_detail', pk=pk)
        mailing = get_object_or_404(Mailing, pk=pk)
        mailing.is_active = not mailing.is_active
        mailing.save(update_fields=['is_active'])
        state = 'включена' if mailing.is_active else 'отключена'
        messages.success(request, f'Рассылка {state}.')
        return redirect('mailings:mailing_detail', pk=pk)


class MailingAttemptListView(OwnerQuerysetMixin, ListView):
    model = MailingAttempt
    template_name = 'mailings/attempt_list.html'
    context_object_name = 'attempts'
    owner_field = 'mailing__owner'
    allow_manager_view_all = True
    paginate_by = 20


class MailingReportView(OwnerQuerysetMixin, ListView):
    model = Mailing
    template_name = 'mailings/report_list.html'
    context_object_name = 'mailings'
    allow_manager_view_all = True

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.annotate(
            attempts_total=Count('attempts'),
            attempts_success=Count('attempts', filter=Q(attempts__status=MailingAttempt.AttemptStatus.SUCCESS)),
            attempts_fail=Count('attempts', filter=Q(attempts__status=MailingAttempt.AttemptStatus.FAIL)),
        )

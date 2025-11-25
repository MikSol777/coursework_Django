from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.views import View
from django.views.generic import TemplateView, UpdateView, FormView, ListView

from .forms import UserLoginForm, UserProfileForm, UserRegistrationForm
from .models import User
from .services import send_activation_email
from mailings.utils import user_is_manager


class ManagerRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not user_is_manager(request.user):
            messages.error(request, 'Недостаточно прав для просмотра страницы.')
            return redirect('mailings:dashboard')
        return super().dispatch(request, *args, **kwargs)


class UserRegisterView(FormView):
    template_name = 'users/register.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.save()
        form.save_m2m()
        self.object = user
        send_activation_email(user, self.request)
        messages.success(self.request, 'На вашу почту отправлено письмо с подтверждением регистрации.')
        return super().form_valid(form)


class UserActivateView(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError):
            user = None

        if user and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save(update_fields=['is_active'])
            messages.success(request, 'Email успешно подтвержден. Теперь вы можете войти.')
        else:
            messages.error(request, 'Не удалось подтвердить email. Попробуйте еще раз.')
        return redirect('users:login')


class UserLoginView(LoginView):
    template_name = 'users/login.html'
    authentication_form = UserLoginForm
    redirect_authenticated_user = True


class UserLogoutView(LogoutView):
    next_page = reverse_lazy('mailings:dashboard')


class ProfileDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'users/profile_detail.html'


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'users/profile_form.html'
    form_class = UserProfileForm
    success_url = reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        return self.request.user


class UserPasswordResetView(PasswordResetView):
    template_name = 'users/password_reset_form.html'
    email_template_name = 'users/password_reset_email.txt'
    subject_template_name = 'users/password_reset_subject.txt'
    success_url = reverse_lazy('users:password_reset_done')


class UserPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'users/password_reset_done.html'


class UserPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'users/password_reset_confirm.html'
    success_url = reverse_lazy('users:password_reset_complete')


class UserPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'users/password_reset_complete.html'


class ServiceUserListView(ManagerRequiredMixin, ListView):
    model = User
    template_name = 'users/user_list.html'
    context_object_name = 'users'
    ordering = ('email',)


class UserBlockToggleView(ManagerRequiredMixin, View):
    def post(self, request, pk):
        target = get_object_or_404(User, pk=pk)
        if target == request.user:
            messages.error(request, 'Нельзя изменить статус собственного аккаунта.')
            return redirect('users:manage')
        if target.is_superuser:
            messages.error(request, 'Нельзя блокировать администратора.')
            return redirect('users:manage')
        target.is_active = not target.is_active
        target.save(update_fields=['is_active'])
        state = 'разблокирован' if target.is_active else 'заблокирован'
        messages.success(request, f'Пользователь {target.email} {state}.')
        return redirect('users:manage')

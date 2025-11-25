from django.contrib.auth.mixins import LoginRequiredMixin

from .utils import user_is_manager


class OwnerQuerysetMixin(LoginRequiredMixin):
    owner_field = 'owner'
    allow_manager_view_all = False

    def get_queryset(self):
        queryset = super().get_queryset()
        if user_is_manager(self.request.user) and self.allow_manager_view_all:
            return queryset
        return queryset.filter(**{self.owner_field: self.request.user})


class OwnerFormMixin(LoginRequiredMixin):
    owner_field = 'owner'

    def form_valid(self, form):
        if not getattr(form.instance, self.owner_field, None):
            setattr(form.instance, self.owner_field, self.request.user)
        return super().form_valid(form)


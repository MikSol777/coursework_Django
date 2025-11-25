from django import forms

from .models import Client, Mailing, Message
from .utils import user_is_manager


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ('email', 'full_name', 'comment')
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ('subject', 'body')
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
        }


class MailingForm(forms.ModelForm):
    start_at = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
    )
    finish_at = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
    )

    class Meta:
        model = Mailing
        fields = ('start_at', 'finish_at', 'status', 'message', 'clients', 'is_active')
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'message': forms.Select(attrs={'class': 'form-select'}),
            'clients': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        user = getattr(self.request, 'user', None)
        if user and not user_is_manager(user):
            self.fields['message'].queryset = Message.objects.filter(owner=user)
            self.fields['clients'].queryset = Client.objects.filter(owner=user)

    def clean(self):
        cleaned_data = super().clean()
        start_at = cleaned_data.get('start_at')
        finish_at = cleaned_data.get('finish_at')
        if start_at and finish_at and finish_at <= start_at:
            raise forms.ValidationError('Дата окончания должна быть позже даты начала.')
        return cleaned_data



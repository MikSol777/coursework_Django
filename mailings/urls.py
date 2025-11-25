from django.urls import path

from .views import (
    ClientCreateView,
    ClientDeleteView,
    ClientDetailView,
    ClientListView,
    ClientUpdateView,
    DashboardView,
    MailingAttemptListView,
    MailingCreateView,
    MailingDeleteView,
    MailingDetailView,
    MailingListView,
    MailingReportView,
    MailingSendView,
    MailingToggleActiveView,
    MailingUpdateView,
    MessageCreateView,
    MessageDeleteView,
    MessageDetailView,
    MessageListView,
    MessageUpdateView,
)

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('clients/', ClientListView.as_view(), name='clients'),
    path('clients/create/', ClientCreateView.as_view(), name='client_create'),
    path('clients/<int:pk>/', ClientDetailView.as_view(), name='client_detail'),
    path('clients/<int:pk>/edit/', ClientUpdateView.as_view(), name='client_edit'),
    path('clients/<int:pk>/delete/', ClientDeleteView.as_view(), name='client_delete'),
    path('messages/', MessageListView.as_view(), name='messages'),
    path('messages/create/', MessageCreateView.as_view(), name='message_create'),
    path('messages/<int:pk>/', MessageDetailView.as_view(), name='message_detail'),
    path('messages/<int:pk>/edit/', MessageUpdateView.as_view(), name='message_edit'),
    path('messages/<int:pk>/delete/', MessageDeleteView.as_view(), name='message_delete'),
    path('mailings/', MailingListView.as_view(), name='mailing_list'),
    path('mailings/create/', MailingCreateView.as_view(), name='mailing_create'),
    path('mailings/<int:pk>/', MailingDetailView.as_view(), name='mailing_detail'),
    path('mailings/<int:pk>/edit/', MailingUpdateView.as_view(), name='mailing_edit'),
    path('mailings/<int:pk>/delete/', MailingDeleteView.as_view(), name='mailing_delete'),
    path('mailings/<int:pk>/send/', MailingSendView.as_view(), name='mailing_send'),
    path('mailings/<int:pk>/toggle/', MailingToggleActiveView.as_view(), name='mailing_toggle'),
    path('attempts/', MailingAttemptListView.as_view(), name='attempts'),
    path('reports/', MailingReportView.as_view(), name='reports'),
]



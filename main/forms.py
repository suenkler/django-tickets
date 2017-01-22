# -*- coding: utf-8 -*-

from django import forms
from django.contrib.auth.models import User

from .models import Ticket, FollowUp, Attachment


class UserSettingsForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email',)


class TicketCreateForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ('title', 'description')


class TicketEditForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ('title', 'owner', 'description',
                  'status', 'waiting_for', 'assigned_to')


class FollowupForm(forms.ModelForm):

    class Meta:
        model = FollowUp
        fields = ('ticket', 'title', 'text', 'user')


class AttachmentForm(forms.ModelForm):
    class Meta:
        model = Attachment
        fields = ('file',)

# -*- coding: utf-8 -*-

from django.shortcuts import render, render_to_response, redirect
from django.template import RequestContext
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.core.mail import send_mail

from .models import Ticket, Attachment, FollowUp
from .forms import UserSettingsForm
from .forms import TicketCreateForm, TicketEditForm, FollowupForm, AttachmentForm

# Logging
import logging
logger = logging.getLogger(__name__)


def inbox_view(request):

    users = User.objects.all()
    tickets_unassigned = Ticket.objects.all().exclude(assigned_to__in=users)
    tickets_assigned = Ticket.objects.filter(assigned_to__in=users)

    return render_to_response('main/inbox.html',
                              {"tickets_assigned": tickets_assigned,
                               "tickets_unassigned": tickets_unassigned, },
                              context_instance=RequestContext(request))


def my_tickets_view(request):

    tickets = Ticket.objects.filter(assigned_to=request.user).exclude(status__exact="DONE")
    tickets_waiting = Ticket.objects.filter(waiting_for=request.user).filter(status__exact="WAITING")

    
    return render_to_response('main/my-tickets.html',
                              {"tickets": tickets,
                               "tickets_waiting": tickets_waiting },
                              context_instance=RequestContext(request))


def all_tickets_view(request):

    tickets_open = Ticket.objects.all().exclude(status__exact="DONE")

    return render_to_response('main/all-tickets.html',
                              {"tickets": tickets_open, },
                              context_instance=RequestContext(request))


def archive_view(request):

    tickets_closed = Ticket.objects.filter(status__exact="DONE")

    return render_to_response('main/archive.html',
                              {"tickets": tickets_closed, },
                              context_instance=RequestContext(request))


def usersettings_update_view(request):

    user = request.user

    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form_user = UserSettingsForm(request.POST)

        # check whether it's valid:
        if form_user.is_valid():

            # Save User model fields
            user.first_name = request.POST['first_name']
            user.last_name = request.POST['last_name']
            user.save()

            # redirect to the index page
            return HttpResponseRedirect(request.GET.get('next', '/inbox/'))

    # if a GET (or any other method) we'll create a blank form
    else:
        form_user = UserSettingsForm(instance=user)

    return render(request, 'main/settings.html', {'form_user': form_user,})


def ticket_create_view(request):

    if request.POST:
        form = TicketCreateForm(request.POST)

        if form.is_valid():

            obj = form.save()
            # set owner
            obj.owner = request.user
            obj.status = "TODO"
            obj.save()

            return redirect('inbox')

    else:
        form = TicketCreateForm()

    return render(request,
                  'main/ticket_edit.html',
                  {'form': form, })


def ticket_edit_view(request, pk):

    data = Ticket.objects.get(id=pk)

    if request.POST:
        form = TicketEditForm(request.POST, instance=data)
        if form.is_valid():

            # set field closed_date to now() if status changed to "DONE"
            if form.cleaned_data['status'] == "DONE":
                data.closed_date = timezone.now()

            form.save()

            return redirect('inbox')

    else:
        form = TicketEditForm(instance=data)

    return render(request,
                  'main/ticket_edit.html',
                  {'form': form, })


def ticket_detail_view(request, pk):

    ticket = Ticket.objects.get(id=pk)
    attachments = Attachment.objects.filter(ticket=ticket)
    followups = FollowUp.objects.filter(ticket=ticket)

    return render(request,
                  'main/ticket_detail.html',
                  {'ticket': ticket,
                   'attachments': attachments,
                   'followups': followups, })


def followup_create_view(request):

    if request.POST:

        form = FollowupForm(request.POST)

        if form.is_valid():
            form.save()

            ticket = Ticket.objects.get(id=request.POST['ticket'])
            # mail notification to owner of ticket
            notification_subject = "[#" + str(ticket.id) + "] New followup"
            notification_body = "Hi,\n\na new followup was created for ticket #" \
                                + str(ticket.id) \
                                + " (http://localhost:8000/ticket/" \
                                + str(ticket.id) \
                                + "/)\n\nTitle: " + form.data['title'] \
                                + "\n\n" + form.data['text']

            send_mail(notification_subject, notification_body, 'test@suenkler.info',
                            [ticket.owner.email], fail_silently=False)

            return redirect('inbox')

    else:
        form = FollowupForm(initial={'ticket': request.GET.get('ticket'),
                                     'user': request.user})

    return render(request,
                  'main/followup_edit.html',
                  {'form': form, })


def followup_edit_view(request, pk):

    data = FollowUp.objects.get(id=pk)

    if request.POST:
        form = FollowupForm(request.POST, instance=data)
        if form.is_valid():
            form.save()

            return redirect('inbox')

    else:
        form = FollowupForm(instance=data)

    return render(request,
                  'main/followup_edit.html',
                  {'form': form, })


def attachment_create_view(request):

    if request.POST:
        form = AttachmentForm(request.POST, request.FILES)

        if form.is_valid():
            attachment = Attachment(
                ticket=Ticket.objects.get(id=request.GET['ticket']),
                file=request.FILES['file'],
                filename=request.FILES['file'].name,
                user=request.user
                #mime_type=form.file.get_content_type(),
                #size=len(form.file),
            )
            attachment.save()

            return redirect('inbox')

    else:
        form = AttachmentForm()

    return render(request,
                  'main/attachment_add.html',
                  {'form': form, })

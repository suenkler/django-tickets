"""
This file was derived from:
https://github.com/rossp/django-helpdesk/blob/master/helpdesk/management/commands/get_email.py

Copyright notice for that original file:

Copyright (c) 2008, Ross Poulton (Trading as Jutda)
All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

    1. Redistributions of source code must retain the above copyright
       notice, this list of conditions and the following disclaimer.

    2. Redistributions in binary form must reproduce the above copyright
       notice, this list of conditions and the following disclaimer in the
       documentation and/or other materials provided with the distribution.

    3. Neither the name of Ross Poulton, Jutda, nor the names of any
       of its contributors may be used to endorse or promote products
       derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import email
import imaplib
import mimetypes
import re
import os
from email.header import decode_header
from email.utils import parseaddr, collapse_rfc2231_value
from optparse import make_option
from email_reply_parser import EmailReplyParser
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from django.contrib.auth.models import User

try:
    from django.utils import timezone
except ImportError:
    from datetime import datetime as timezone

from main.models import Ticket, Attachment, FollowUp


class Command(BaseCommand):
    def __init__(self):
        BaseCommand.__init__(self)

        self.option_list += (
            make_option(
                '--quiet', '-q',
                default=False,
                action='store_true',
                help='Hide details about each message as they are processed.'),
            )

    help = 'Process email inbox and create tickets.'

    def handle(self, *args, **options):
        quiet = options.get('quiet', False)
        process_inbox(quiet=quiet)


def process_inbox(quiet=False):
    """
    Process IMAP inbox
    """
    server = imaplib.IMAP4_SSL(os.environ["DJANGO_TICKET_INBOX_SERVER"], 993)
    server.login(os.environ["DJANGO_TICKET_INBOX_USER"], os.environ["DJANGO_TICKET_INBOX_PASSWORD"])
    server.select("INBOX")
    status, data = server.search(None, 'NOT', 'DELETED')
    if data:
        msgnums = data[0].split()
        for num in msgnums:
            status, data = server.fetch(num, '(RFC822)')
            ticket = ticket_from_message(message=data[0][1], quiet=quiet)
            if ticket:
                server.store(num, '+FLAGS', '\\Deleted')
    server.expunge()
    server.close()
    server.logout()


def decodeUnknown(charset, string):
    if not charset:
        try:
            return string.decode('utf-8', 'ignore')
        except:
            return string.decode('iso8859-1', 'ignore')
    return unicode(string, charset)


def decode_mail_headers(string):
    decoded = decode_header(string)
    return u' '.join([unicode(msg, charset or 'utf-8') for msg, charset in decoded])


def ticket_from_message(message, quiet):
    """
    Create a ticket or a followup (if ticket id in subject)
    """
    msg = message
    message = email.message_from_string(msg)
    subject = message.get('subject', 'Created from e-mail')
    subject = decode_mail_headers(decodeUnknown(message.get_charset(), subject))
    sender = message.get('from', ('Unknown Sender'))
    sender = decode_mail_headers(decodeUnknown(message.get_charset(), sender))
    sender_email = parseaddr(sender)[1]
    body_plain, body_html = '', ''

    matchobj = re.match(r".*\["+"-(?P<id>\d+)\]", subject)
    if matchobj:
        # This is a reply or forward.
        ticket = matchobj.group('id')
    else:
        ticket = None

    counter = 0
    files = []

    for part in message.walk():
        if part.get_content_maintype() == 'multipart':
            continue

        name = part.get_param("name")
        if name:
            name = collapse_rfc2231_value(name)

        if part.get_content_maintype() == 'text' and name == None:
            if part.get_content_subtype() == 'plain':
                body_plain = EmailReplyParser.parse_reply(decodeUnknown(part.get_content_charset(), part.get_payload(decode=True)))
            else:
                body_html = part.get_payload(decode=True)
        else:
            if not name:
                ext = mimetypes.guess_extension(part.get_content_type())
                name = "part-%i%s" % (counter, ext)

            files.append({
                'filename': name,
                'content': part.get_payload(decode=True),
                'type': part.get_content_type()},
            )

        counter += 1

    if body_plain:
        body = body_plain
    else:
        body = 'No plain-text email body available. Please see attachment email_html_body.html.'

    if body_html:
        files.append({
            'filename': 'email_html_body.html',
            'content': body_html,
            'type': 'text/html',
        })

    now = timezone.now()

    if ticket:
        try:
            t = Ticket.objects.get(id=ticket)
            new = False
        except Ticket.DoesNotExist:
            ticket = None

    if ticket == None:

        # set owner depending on sender_email
        # list of all email addresses from the user model
        users = User.objects.all()
        email_addresses = []
        for user in users:
            email_addresses.append(user.email)

        ############################################################
        # if ticket id in subject => new followup instead of new ticket
        tickets = Ticket.objects.all()
        ticket_ids = []
        for ticket in tickets:
            ticket_ids.append(ticket.id)

        # extract id from subject
        subject_id = re.search(r'\[#(\d*)\]\s.*', subject)
        try:
            subject_id = subject_id.group(1)
        except:
            subject_id = "0000"  # no valid id

        # if there was an ID in the subject, create followup
        if int(subject_id) in ticket_ids:

            if sender_email in email_addresses:
                f = FollowUp(
                           title=subject,
                           created=now,
                           text=body,
                           ticket=Ticket.objects.get(id=subject_id),
                           user=User.objects.get(email=sender_email),
                )
            else:
                f = FollowUp(
                           title=subject,
                           created=now,
                           text=body,
                           ticket=Ticket.objects.get(id=subject_id),
                )

            f.save()

        # if no ID in the subject, create ticket
        else:

            # if known sender, set also the field owner
            if sender_email in email_addresses:
                t = Ticket(
                           title=subject,
                           status="TODO",
                           created=now,
                           description=body,
                           owner=User.objects.get(email=sender_email),
                )
            # if unknown sender, skip the field owner
            else:
                t = Ticket(
                           title=subject,
                           status="TODO",
                           created=now,
                           description=body,
                )

            t.save()

            from django.core.mail import send_mail
            notification_subject = "[#" + str(t.id) + "] New ticket created"
            notification_body = "Hi,\n\na new ticket was created: http://localhost:8000/ticket/" \
                                + str(t.id) + "/"
            send_mail(notification_subject, notification_body, os.environ["DJANGO_TICKET_EMAIL_NOTIFICATIONS_FROM"],
                            [os.environ["DJANGO_TICKET_EMAIL_NOTIFICATIONS_TO"]], fail_silently=False)

        ############################################################

        new = True
        update = ''

    elif t.status == Ticket.CLOSED_STATUS:
        t.status = Ticket.REOPENED_STATUS
        t.save()

    # files of followups should be assigned to the corresponding ticket
    for file in files:

        if file['content']:

            filename = file['filename'].encode('ascii', 'replace').replace(' ', '_')
            filename = re.sub('[^a-zA-Z0-9._-]+', '', filename)

            # if followup
            if int(subject_id) in ticket_ids:
                a = Attachment(
                           ticket=Ticket.objects.get(id=subject_id),
                           filename=filename,
                           #mime_type=file['type'],
                           #size=len(file['content']),
                )

            # if new ticket
            else:
                a = Attachment(
                           ticket=t,
                           filename=filename,
                           #mime_type=file['type'],
                           #size=len(file['content']),
                )

            a.file.save(filename, ContentFile(file['content']), save=False)
            a.save()

            if not quiet:
                print " - %s" % filename

    if int(subject_id) in ticket_ids:
        return f
    else:
        return t


if __name__ == '__main__':
    process_email()

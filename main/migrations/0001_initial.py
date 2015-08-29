# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import main.models
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('file', models.FileField(upload_to=main.models.attachment_path, max_length=1000, verbose_name=b'File')),
                ('filename', models.CharField(max_length=1000, verbose_name=b'Filename')),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Attachment',
                'verbose_name_plural': 'Attachments',
            },
        ),
        migrations.CreateModel(
            name='FollowUp',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(default=django.utils.timezone.now, verbose_name=b'Date')),
                ('title', models.CharField(max_length=200, verbose_name=b'Title')),
                ('text', models.TextField(null=True, verbose_name=b'Text', blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-modified'],
            },
        ),
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255, verbose_name=b'Title')),
                ('description', models.TextField(null=True, verbose_name=b'Description', blank=True)),
                ('status', models.CharField(blank=True, max_length=255, null=True, verbose_name=b'Status', choices=[(b'TODO', b'TODO'), (b'IN PROGRESS', b'IN PROGRESS'), (b'WAITING', b'WAITING'), (b'DONE', b'DONE')])),
                ('closed_date', models.DateTimeField(null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('assigned_to', models.ForeignKey(related_name='assigned_to', verbose_name=b'Assigned to', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('owner', models.ForeignKey(related_name='owner', verbose_name=b'Owner', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('waiting_for', models.ForeignKey(related_name='waiting_for', verbose_name=b'Waiting For', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='followup',
            name='ticket',
            field=models.ForeignKey(verbose_name=b'Ticket', to='main.Ticket'),
        ),
        migrations.AddField(
            model_name='followup',
            name='user',
            field=models.ForeignKey(verbose_name=b'User', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='attachment',
            name='ticket',
            field=models.ForeignKey(verbose_name=b'Ticket', to='main.Ticket'),
        ),
        migrations.AddField(
            model_name='attachment',
            name='user',
            field=models.ForeignKey(verbose_name=b'User', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]

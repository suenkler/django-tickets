# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url
from django.contrib import admin

import main.views
from django.contrib.auth.decorators import login_required

# to include media files at the end
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = patterns(
    '',

    # Login and settings pages
    url(r'^$', 'django.contrib.auth.views.login'),

    url(r'^logout/$', 'django.contrib.auth.views.logout_then_login'),

    url(r'^settings/$',
        login_required(main.views.usersettings_update_view),
        name='user-settings'),

    # Django admin
    url(r'^admin/', include(admin.site.urls)),

    # create new ticket
    url(r'^ticket/new/$',
        login_required(main.views.ticket_create_view),
        name='ticket_new'),

    # edit ticket
    url(r'^ticket/edit/(?P<pk>\d+)/$',
        login_required(main.views.ticket_edit_view),
        name='ticket_edit'),

    # view ticket
    url(r'^ticket/(?P<pk>\d+)/$',
        login_required(main.views.ticket_detail_view),
        name='ticket_detail'),

    # create new followup
    url(r'^followup/new/$',
        login_required(main.views.followup_create_view),
        name='followup_new'),

    # edit followup
    url(r'^followup/edit/(?P<pk>\d+)/$',
        login_required(main.views.followup_edit_view),
        name='followup_edit'),

    # create new attachment
    url(r'^attachment/new/$',
        login_required(main.views.attachment_create_view),
        name='attachment_new'),

    # ticket overviews
    url(r'^inbox/$',
        login_required(main.views.inbox_view),
        name='inbox'),

    url(r'^my-tickets/$',
        login_required(main.views.my_tickets_view),
        name='my-tickets'),

    url(r'^all-tickets/$',
        login_required(main.views.all_tickets_view),
        name='all-tickets'),

    url(r'^archive/$',
        login_required(main.views.archive_view),
        name='archive'),

) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

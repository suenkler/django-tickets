from django.contrib import admin
from .models import Ticket, FollowUp, Attachment


class TicketAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'title',
                    'description',
                    'assigned_to',
                    'created',
                    'updated',)


# Register Models
admin.site.register(Ticket, TicketAdmin)
admin.site.register(FollowUp)
admin.site.register(Attachment)

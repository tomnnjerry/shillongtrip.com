from django.contrib import admin

from .models import Enquiry


@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display = ('created', 'name', 'phone', 'month', 'tour', 'source', 'handled')
    list_filter = ('handled', 'source', 'month')
    search_fields = ('name', 'phone', 'email', 'tour', 'message')
    list_editable = ('handled',)
    readonly_fields = ('created', 'attribution')
    date_hierarchy = 'created'


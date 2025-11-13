from django.contrib import admin
from .models import Application, ApplicationDocument, ApplicationStatusHistory

# Register your models here.
@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('application_number', 'created_by', 'current_status', 'associated_property')
    search_fields = ('created_by__username', 'current_status', 'associated_property__address')
    list_filter = ('current_status', 'submission_date', 'created_by')

@admin.register(ApplicationDocument)
class ApplicationDocumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'application', 'document_category', 'upload_date')
    search_fields = ('document_category', 'file_name')
    list_filter = ('document_category', 'upload_date')

@admin.register(ApplicationStatusHistory)
class ApplicationStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'application', 'from_status', 'to_status', 'changed_by', 'changed_at')
    search_fields = ('application__applicant_name', 'from_status', 'to_status', 'changed_by__username')
    list_filter = ('from_status', 'to_status', 'changed_at')
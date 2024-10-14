from django.contrib import admin
from .models import DataUploadLog

@admin.register(DataUploadLog)
class DataUploadLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'upload_time', 'file_name', 'status', 'rows_processed')

from django.contrib import admin
from .models import dataOffice, dataOfficial

@admin.register(dataOffice)
class OfficeAdmin(admin.ModelAdmin):
    list_display = ('id', 'parentId', 'hierarchies', 'officename', 'currentRegulations')

@admin.register(dataOfficial)
class OfficialAdmin(admin.ModelAdmin):
    list_display = ('id', 'office', 'name')

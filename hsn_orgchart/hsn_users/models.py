from django.db import models
from django.contrib.auth.models import User

class DataUploadLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # The user who uploaded the file
    upload_time = models.DateTimeField(auto_now_add=True)  # Time of upload
    file_name = models.CharField(max_length=255)  # Name of the uploaded file
    rows_processed = models.IntegerField()  # Number of rows processed (optional, for additional info)
    status = models.CharField(max_length=50, choices=[('SUCCESS', 'Success'), ('FAILED', 'Failed')])  # Upload status
    error_message = models.TextField(blank=True, null=True)  # Details about any errors (if applicable)

    def __str__(self):
        return f"Upload by {self.user} on {self.upload_time} - Status: {self.status}"

class dataOffice(models.Model):
    parentId = models.IntegerField(null=True, blank=True)
    hierarchies = models.CharField(max_length=10)
    officename = models.CharField(max_length=255)
    currentRegulations = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.officename

class dataOfficial(models.Model):
    office = models.ForeignKey(dataOffice, on_delete=models.CASCADE)  # Use 'dataOffice' here to reference the correct model
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

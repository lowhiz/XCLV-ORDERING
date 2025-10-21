from django.db import models
import uuid #for unique identifier

class Batch(models.Model):
    batchID = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) #Batch Unique Id
    batchName = models.CharField(max_length=16, unique=True) #Batch A to Batch Z
    batchStatus = models.BooleanField(default=False)    #Batch status

    def __str__(self):
        return self.batchName

class QrCode(models.Model):
    unique_token = models.CharField(max_length=255, unique=True)
    batch = models.ForeignKey('Batch', on_delete=models.CASCADE, related_name='qrcodes')
    image = models.ImageField(upload_to='qrcodes/')

    def __str__(self):
        return self.unique_token
    
class ValidList(models.Model):
    unique_token = models.CharField(max_length=255, unique=True)
    
    def __str__(self):
        return self.unique_token
    
class InvalidList(models.Model):
    unique_token = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.unique_token

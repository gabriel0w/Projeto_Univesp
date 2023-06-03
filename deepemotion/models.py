from django.db import models

class Person(models.Model):
    name = models.CharField(max_length=255)
    emotion1 = models.CharField(max_length=255)
    emotion2 = models.CharField(max_length=255)
    createDate = models.DateTimeField(auto_now_add=True)

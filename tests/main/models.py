from django.db import models

# Create your models here.

class Author(models.Model):
    name = models.CharField(max_length=64, null=False, blank=False)

class Item(models.Model):
    text = models.CharField(max_length=64, null=False, blank=False)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)

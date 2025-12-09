from django.db import models

class Pet(models.Model):
    name = models.CharField(max_length=100)
    species = models.CharField(max_length=100)
    age = models.IntegerField()
    owner = models.CharField(max_length=100)
    vaccinated = models.BooleanField(default=False)

    def __str__(self):
        return self.name

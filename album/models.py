from django.db import models
from actor.models import Actor

class Album(models.Model):
    code = models.CharField(max_length=255, unique=True, null=False)
    title = models.CharField(max_length=255, unique=True, null=False)
    year = models.IntegerField(null=False)
    thumbnail300x300 = models.CharField(max_length=10000, null=False)
    thumbnail1200x1200 = models.CharField(max_length=10000, null=False)

    actors = models.ManyToManyField(Actor, related_name='albums')

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.title
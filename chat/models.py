from django.db import models
from django.conf import settings


class Message(models.Model):
    content = models.CharField(max_length=500, blank=False, null=False)
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, related_name='receiver')
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, related_name='sender')
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        # by default order by date_created (ASC)
        ordering = ('date_created',)

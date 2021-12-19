from django.db import models
from django.contrib.auth.models import User
from django.core.mail import send_mail


class Census(models.Model):
    voting_id = models.PositiveIntegerField()
    voter_id = models.PositiveIntegerField()

    class Meta:
        unique_together = (('voting_id', 'voter_id'),)

    def save(self, *args, **kwargs):
        return super().save()
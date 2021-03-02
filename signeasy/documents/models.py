import uuid

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models


class Document(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=63, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)
    is_locked = models.BooleanField(default=False)


class Event(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True)
    document = models.UUIDField(null=False)
    action = models.CharField(max_length=31, null=False)
    updated_at = models.DateTimeField(auto_now_add=True)


class Access(models.Model):
    ROLES = [
        ('OWNER', 'owner'),
        ('COLLABORATOR', 'collaborator'),
    ]

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True)
    document = models.ForeignKey(to='Document', on_delete=models.CASCADE, null=True)
    role = models.CharField(max_length=31, choices=ROLES, default='OWNER', null=True)
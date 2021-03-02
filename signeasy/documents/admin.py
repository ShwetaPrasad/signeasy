from django.contrib import admin
from .models import Access, Document, Event
# Register your models here.

admin.site.register(Access)
admin.site.register(Document)
admin.site.register(Event)
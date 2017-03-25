from django.contrib import admin
from .models import LocalCredentials, RemoteCredentials

# Register your models here.
admin.site.register(LocalCredentials)
admin.site.register(RemoteCredentials)

from django.contrib import admin

from .models import Account, Estimate, DataFile

admin.site.register(Account)
admin.site.register(Estimate)
admin.site.register(DataFile)

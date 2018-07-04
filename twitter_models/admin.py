from django.contrib import admin

from .models import Account, Estimate, DataFile, Prediction

admin.site.register(Account)
admin.site.register(Estimate)
admin.site.register(DataFile)
admin.site.register(Prediction)

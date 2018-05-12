from django.contrib import admin

from .models import Job
from .models import UserPublicKey


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    pass

@admin.register(UserPublicKey)
class UserPublicKeyAdmin(admin.ModelAdmin):
    pass

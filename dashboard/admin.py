from django.contrib import admin

from .models import Job
from .models import UserPublicKey
from .models import Rpc


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    pass

@admin.register(UserPublicKey)
class UserPublicKeyAdmin(admin.ModelAdmin):
    pass

@admin.register(Rpc)
class RpcAdmin(admin.ModelAdmin):
    pass

from django.contrib import admin
from .models import OTP, Authentication

admin.site.register(Authentication)
admin.site.register(OTP)
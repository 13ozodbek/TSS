from django.contrib import admin
from .models import OTP, Authentication, FollowUser

admin.site.register(Authentication)
admin.site.register(OTP)
admin.site.register(FollowUser)
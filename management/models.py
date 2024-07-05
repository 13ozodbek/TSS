import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser

gender_types = (
    (1, 'male'),
    (2, 'female'),
    (3, 'other'),
)

otp_types = (
    (1, 'register'),
    (2, 'resend'),
    (3, 'reset'),
)

class Authentication(AbstractUser):
    username = models.CharField(unique=True, max_length=255)
    image = models.ImageField(upload_to='images/')
    age = models.IntegerField(default=1)
    gender = models.IntegerField(choices=gender_types, default=1)


    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.username

class OTP(models.Model):
    otp_user = models.CharField(max_length=50, unique=True)
    otp_code = models.IntegerField(default=0)
    otp_key = models.UUIDField(default=uuid.uuid4, editable=False)
    otp_type = models.IntegerField(choices=otp_types, default=1)
    otp_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.otp_user)


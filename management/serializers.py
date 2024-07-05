from .models import Authentication, OTP
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Authentication
        fields = ('username', 'email', 'first_name', 'last_name', 'password')




class OTPVerifySerializer(serializers.Serializer):
    otp_code = serializers.IntegerField(min_value=1000, max_value=9999)
    otp_user = serializers.CharField()



class OTPRegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = OTP
        fields = ('username', 'email', 'first_name', 'last_name', 'password')

class OTPResendVerifySerializer(serializers.Serializer):
    otp_user = serializers.CharField()


class ResetPasswordSerializer(serializers.Serializer):
    username = serializers.CharField()
    class Meta:
        fields = ('username')

class VerifyResettingSerializer(serializers.Serializer):
    otp_code = serializers.IntegerField(min_value=1000, max_value=9999)
    username = serializers.CharField()
    password = serializers.CharField()
    password_repeat = serializers.CharField()
    class Meta:
        fields = ('otp_code', 'username', 'password', 'password_repeat')

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


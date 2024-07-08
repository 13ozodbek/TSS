from django.contrib.auth.hashers import make_password

from .models import Authentication, OTP
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    password_re = serializers.CharField(write_only=True)

    class Meta:
        model = Authentication
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'password',
            'password_re',
            'age',
            'workplace',
            'gender',
            'image')

        extra_kwargs = {
            'password': {'write_only': True,
                         'required': False},
        }



class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Authentication
        fields = (
            'first_name',
            'last_name',
            'age',
            'workplace',
            'gender',
            'image',
            'password',
        )
        extra_kwargs = {
            'password': {'write_only': True,
                         'required': False},
        }

    def profile_update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.image = validated_data.get('image', instance.profile_picture)
        instance.workplace = validated_data.get('company', instance.company)
        instance.email = validated_data.get('email', instance.email)
        instance.age = validated_data.get('age', instance.age)
        instance.gender = validated_data.get('gender', instance.gender)
        #instance.password = make_password((validated_data.get('password')), instance.password)
        instance.save()
        return instance


class OTPVerifySerializer(serializers.Serializer):
    otp_code = serializers.IntegerField(min_value=1000,
                                        max_value=9999)
    otp_user = serializers.CharField()


class OTPRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = OTP
        fields = ('username',
                  'email',
                  'first_name',
                  'last_name',
                  'password')


class OTPResendVerifySerializer(serializers.Serializer):
    otp_user = serializers.CharField()


class ResetPasswordSerializer(serializers.Serializer):
    username = serializers.CharField()

    class Meta:
        fields = ('username')


class VerifyResettingSerializer(serializers.Serializer):
    otp_code = serializers.IntegerField(min_value=1000,
                                        max_value=9999)
    username = serializers.CharField()
    password = serializers.CharField()
    password_repeat = serializers.CharField()

    class Meta:
        fields = ('otp_code',
                  'username',
                  'password',
                  'password_repeat')


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

# class AuthMicroservicesSerializer(serializers.Serializer):
#     uuid = serializers.CharField()

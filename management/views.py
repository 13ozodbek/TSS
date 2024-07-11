from math import floor
import jwt
import requests
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
import datetime
from datetime import datetime
from rest_framework_simplejwt.authentication import JWTAuthentication

from config.settings import SECRET_KEY
from .models import (Authentication,
                     OTP)
from .serializers import (UserSerializer,
                          OTPVerifySerializer,
                          OTPResendVerifySerializer,
                          ResetPasswordSerializer,
                          VerifyResettingSerializer,
                          LoginSerializer,
                          UpdateUserSerializer,
                          AuthMeSerializer, UserOperationsSerializer
                          )
from .utils import (check_otp_expire,
                    generate_random_number,
                    send_otp_code,
                    )
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import login
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken


class Register(ViewSet):
    @swagger_auto_schema(
        operation_description="Register",
        operation_summary="Register new users",
        responses={201: ''},
        request_body=UserSerializer,
        tags=['auth']
    )
    def register(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            if serializer.validated_data['password_re'] != serializer.validated_data['password']:
                return Response({'error': 'Passwords do not match'},
                                status=status.HTTP_400_BAD_REQUEST)

            save_user_info = Authentication.objects.create(username=serializer.validated_data['username'],
                                                           password=make_password(
                                                               serializer.validated_data['password']),
                                                           first_name=serializer.validated_data['first_name'],
                                                           last_name=serializer.validated_data['last_name'],
                                                           email=serializer.validated_data.get('email'),
                                                           age=serializer.validated_data.get('age'),
                                                           gender=serializer.validated_data.get('gender'),
                                                           workplace=serializer.validated_data.get('workplace'), )
            save_user_info.save()

            otp = OTP.objects.create(otp_user=serializer.validated_data['username'],
                                     otp_code=generate_random_number())
            otp.save()
            send_otp_code(otp)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)

        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Verify",
        operation_summary="Verify user status by OTP",
        responses={200: ''},
        request_body=OTPVerifySerializer,
        tags=['auth']
    )
    def verify(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            otp_obj = OTP.objects.filter(otp_user=serializer.data['otp_user']).first()
            if not check_otp_expire(otp_obj):
                otp_obj.delete()
                return Response({'code expired'},
                                status=status.HTTP_400_BAD_REQUEST)

            if serializer.is_valid(raise_exception=True):
                check_code_and_key = OTP.objects.filter(otp_code=serializer.data['otp_code'],
                                                        otp_user=serializer.data['otp_user']).first()
                if check_code_and_key:
                    user = Authentication.objects.filter(username=check_code_and_key.otp_user).first()
                    user.is_verified = True
                    user.save(update_fields=['is_verified'])
                    OTP.objects.filter(otp_user=otp_obj.otp_user).delete()

                return Response(data={f'{serializer.data['otp_user']}': 'user verified'},
                                status=status.HTTP_200_OK)

        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Resend OTP code",
        operation_summary="Resen user new OTP",
        responses={200: ''},
        request_body=OTPResendVerifySerializer,
        tags=['auth']
    )
    def resend(self, request, *args, **kwargs):
        serializer = OTPResendVerifySerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            previous_code = OTP.objects.filter(otp_user=serializer.data['otp_user']).first()
            existing_user = Authentication.objects.filter(username=serializer.data['otp_user']).first()

            if existing_user.is_verified:
                return Response({'user already verified'},
                                status=status.HTTP_200_OK)
            if check_otp_expire(previous_code):
                current = datetime.datetime.now(datetime.timezone.utc)
                untill = datetime.timedelta(seconds=60) + previous_code.otp_created
                time_difference = current - untill
                time_difference = floor(time_difference.total_seconds())
                return Response({f'Try again after {time_difference} seconds'},
                                status=status.HTTP_400_BAD_REQUEST)

            if previous_code:
                previous_code.delete()

            new_code = OTP.objects.create(otp_user=serializer.data['otp_user'],
                                          otp_type=2,
                                          otp_code=generate_random_number(), )
            send_otp_code(new_code)
            new_code.save()

            return Response({'new code sent'},
                            status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPassword(ViewSet):
    @swagger_auto_schema(
        operation_description="Reset password",
        operation_summary="Reset password, send OTP",
        responses={200: ''},
        request_body=ResetPasswordSerializer,
        tags=['auth']
    )
    def reset_password(self, request):
        serializer = ResetPasswordSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            user_existence_check = Authentication.objects.filter(username=serializer.data['username']).first()

            if not user_existence_check:
                return Response({'error': 'User does not exist'},
                                status=status.HTTP_400_BAD_REQUEST)
            new_otp = OTP.objects.create(otp_user=serializer.data['username'],
                                         otp_code=generate_random_number(),
                                         otp_type=3)
            new_otp.save()
            send_otp_code(new_otp)
        return Response('code sent', status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Reset/Set new password",
        operation_summary="Set new password",
        responses={201: ''},
        request_body=VerifyResettingSerializer,
        tags=['auth']
    )
    def verify_resetting(self, request, *args, **kwargs):
        serializer = VerifyResettingSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            otp_check = OTP.objects.filter(otp_user=serializer.data['username'],
                                           otp_code=serializer.data['otp_code']).first()

            if serializer.data['password'] != serializer.data['password_repeat']:
                return Response({'error': 'Passwords do not match'})

            if not check_otp_expire(otp_check):
                return Response({'code expired'}, )

            if otp_check:
                user = Authentication.objects.filter(username=serializer.data['username']).first()
                user.password = make_password(serializer.data['password'])
                user.save(update_fields=['password'])
                otp_check.delete()

                return Response('password changed',
                                status=status.HTTP_200_OK)
            return Response('otp code or user does not exist',
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)


class UpdateProfile(ViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        operation_description="Update profile",
        operation_summary="Update user's info",
        request_body=UpdateUserSerializer,
        responses={200: ''},
        tags=['auth']
    )
    def update_profile(self, request):
        user = request.user
        serializer = UpdateUserSerializer(user, data=request.data)

        if not user.is_authenticated:
            return Response({'error': 'Not logged in'}, status=status.HTTP_400_BAD_REQUEST)

        if serializer.is_valid(raise_exception=True):
            password = serializer.validated_data.get('password')
            if password:
                serializer.validated_data['password'] = make_password(password)
            serializer.save()
            return Response('user information changed', status=status.HTTP_200_OK)

        return Response({'error': 'User does not exist or not authorised'},
                        status=status.HTTP_400_BAD_REQUEST)


class Login(ViewSet):
    @swagger_auto_schema(
        operation_description="Log in ",
        operation_summary="Login verified user",
        responses={200: 'access and refresh tokens'},
        request_body=LoginSerializer,
        tags=['auth']
    )
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = Authentication.objects.filter(username=serializer.validated_data['username']).first()

            if not (user or user.is_verified):
                return Response({'error': 'User does not exist or not verified'})

            if not check_password(serializer.data['password'],
                                  user.password):
                return Response({'error': 'Passwords do not match'},
                                status=status.HTTP_400_BAD_REQUEST)

            token = AccessToken.for_user(user)
            refresh_token = RefreshToken.for_user(user)

            login(request, user)

            return Response({'message': 'login successful',
                             'access': f'{token}',
                             'refresh': f'{refresh_token}'},

                            status=status.HTTP_200_OK)

        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)


class UserInfoView(ViewSet):

    @swagger_auto_schema(
        operation_description="User info",
        operation_summary="Return user info by token",
        responses={200: 'User Information'},
        request_body=AuthMeSerializer,
        tags=['auth']
    )
    def auth_me(self, request, *args, **kwargs):
        serializer = AuthMeSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            token_uuid = serializer.validated_data['token']
            check_data = {"token": f"{token_uuid}"}
            check_authentication = requests.post('http://134.122.76.27:8114/api/v1/check/', json=check_data)

            if not check_authentication.status_code == 200:
                return Response({'error': 'Unidentified API'}, status=status.HTTP_400_BAD_REQUEST)

            token = request.META.get('HTTP_AUTHORIZATION', " ")
            if not token:
                return Response({'error': 'Token not found'},
                                status=status.HTTP_400_BAD_REQUEST)
            token = token.split()[1]
            decoded_token = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])

            id = decoded_token.get('user_id')
            serializer = UserSerializer(Authentication.objects.filter(id=id).first())

            return Response(serializer.data,
                            status=status.HTTP_200_OK)

        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)


class UserOperations(ViewSet):
    @swagger_auto_schema(
        operation_description="Operations on users",
        operation_summary="Return all users",
        responses={200: 'Operation is completed'},
        request_body=AuthMeSerializer,
        tags=['get']
    )
    def get_users(self, request):
        serializer = AuthMeSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            token_uuid = serializer.validated_data['token']
            check_data = {"token": f"{token_uuid}"}
            check_authentication = requests.post('http://134.122.76.27:8114/api/v1/check/',
                                                 json=check_data)

            if not check_authentication.status_code == 200:
                return Response({'error': 'Unidentified API'},
                                status=status.HTTP_400_BAD_REQUEST)

            users = Authentication.objects.all()
            return Response(users.data,
                            status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Operations on users",
        operation_summary="return user info",
        responses={200: 'Operation is completed'},
        request_body=UserOperationsSerializer,
        tags=['get']
    )
    def get_user_by_id(self, request):

        token_uuid = request.data['token']
        check_data = {"token": f"{token_uuid}"}
        check_authentication = requests.post('http://134.122.76.27:8114/api/v1/check/',
                                             json=check_data)
        if not check_authentication.status_code == 200:
            return Response({'error': 'Unidentified API'},
                            status=status.HTTP_400_BAD_REQUEST)

        user = Authentication.objects.filter(id=request.data['user_id']).first()
        if not user:
            return Response({'error': 'User does not exist'},
                            status=status.HTTP_400_BAD_REQUEST)
        serializer = UserSerializer(user)
        return Response(serializer.data,
                        status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Operations on users",
        operation_summary="delete user",
        responses={200: 'Operation is completed'},
        request_body=UserOperationsSerializer
    )
    def delete_user_by_id(self, request):

        token_uuid = request.data['token']
        check_data = {"token": f"{token_uuid}"}
        check_authentication = requests.post('http://134.122.76.27:8114/api/v1/check/',
                                             json=check_data)
        if not check_authentication.status_code == 200:
            return Response({'error': 'Unidentified API'},
                            status=status.HTTP_400_BAD_REQUEST)
        user = Authentication.objects.get(id=request.data['user_id']).first()
        if not user:
            return Response({'error': 'User does not exist'},
                            status=status.HTTP_400_BAD_REQUEST)
        user.delete()
        return Response(status=status.HTTP_200_OK)

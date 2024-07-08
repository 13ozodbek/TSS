from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView

from .views import Register, Login, ResetPassword, UpdateProfile, UserInfoView

urlpatterns = [
    path('api/refresh/', TokenRefreshView.as_view(), name='refresh'),
    path('api/get/', TokenObtainPairView.as_view(), name='token_obtain_pair'),

    path('auth/register/', Register.as_view({'post': 'register'})),
    path('auth/verify/', Register.as_view({'post': 'verify'})),

    path('auth/resend/', Register.as_view({'post': 'resend'})),

    path('auth/reset/', ResetPassword.as_view({'post': 'reset_password'})),
    path('auth/verify/resetting/', ResetPassword.as_view({'post': 'verify_resetting'})),

    path('auth/update/', UpdateProfile.as_view({'patch': 'update_profile'})),

    path('auth/login/', Login.as_view({'post': 'login'})),

    path('auth/me/',UserInfoView.as_view({'post':'auth_me'})),





]

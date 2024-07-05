from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView

from .views import Register, Login, ResetAndUpdate

urlpatterns = [
    path('api/refresh/', TokenRefreshView.as_view(), name='refresh'),
    path('api/get/', TokenObtainPairView.as_view(), name='token_obtain_pair'),

    path('auth/register/', Register.as_view({'post': 'register'})),
    path('auth/verify/', Register.as_view({'post': 'verify'})),

    path('auth/resend/', Register.as_view({'post': 'resend'})),

    path('auth/reset/', ResetAndUpdate.as_view({'post': 'reset_password'})),
    path('auth/verify-resetting/', ResetAndUpdate.as_view({'post': 'verify_resetting'})),

    path('auth/update/', ResetAndUpdate.as_view({'post': 'update_password'})),

    path('auth/login/', Login.as_view({'post': 'login'})),




]

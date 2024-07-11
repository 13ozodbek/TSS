from django.conf import settings
from django.urls import path, re_path
from .views import Register, Login, ResetPassword, UpdateProfile, UserInfoView, UserOperations
from django.views.static import serve
urlpatterns = [


    path('auth/register/', Register.as_view({'post': 'register'})),
    path('auth/verify/', Register.as_view({'post': 'verify'})),

    path('auth/resend/', Register.as_view({'post': 'resend'})),

    path('auth/reset/', ResetPassword.as_view({'post': 'reset_password'})),
    path('auth/verify/resetting/', ResetPassword.as_view({'post': 'verify_resetting'})),

    path('auth/update/', UpdateProfile.as_view({'patch': 'update_profile'})),

    path('auth/login/', Login.as_view({'post': 'login'})),

    path('auth/me/',UserInfoView.as_view({'post':'auth_me'})),

    path('get/users/', UserOperations.as_view({'post':'get_users'})),
    path('get/user/id/', UserOperations.as_view({'post':'get_user_by_id'})),
    path('delete/user/', UserOperations.as_view({'delete':'delete_user_by_id'})),

    re_path(r'media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r'static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),





]

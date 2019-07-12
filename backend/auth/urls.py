from django.urls import path, include
from oauth2_provider.views import AuthorizationView
from rest_framework_social_oauth2.views import ConvertTokenView


from auth import views

urlpatterns = [
    path(r'authorize', AuthorizationView.as_view(), name='authorize'),
    path(r'token/', views.token, name="token"),
    path(r'revoke-token/', views.revoke_token, name="revoke-token"),
    path('', include('social_django.urls', namespace="social")),
    path(r'convert-token/', ConvertTokenView.as_view(),
         name="auth-convert-token")
]

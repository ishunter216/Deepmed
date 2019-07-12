from django.contrib import admin
from django.urls import path, include

api_urlpatterns = [
    path('auth/', include('auth.urls')),
    path('accounts/', include('accounts.urls')),
    path('diagnosis/', include('base.urls')),
]

urlpatterns = [
    path('api/v1/', include(api_urlpatterns)),
    path('admin/', admin.site.urls),
]

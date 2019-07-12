from django.urls import path, include

import accounts.views
from common.drf.routers import NoLookupFieldRouter

user_router = NoLookupFieldRouter(trailing_slash=True)
user_router.register('user', accounts.views.UsersViewSet,
                     base_name='users')

urlpatterns = [
    path('', include(user_router.urls)),
]

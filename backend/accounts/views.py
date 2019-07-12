from rest_framework import status, mixins, permissions
from rest_framework.decorators import list_route
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

import accounts.models
import accounts.serializers
from common.drf.mixins import ActionPermissionClassesMixin
from common.drf.permissions import NotAuthenticated


class UsersViewSet(ActionPermissionClassesMixin,
                   mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin,
                   GenericViewSet):
    model = accounts.models.User
    serializer_class = accounts.serializers.UserSerializer
    action_permission_classes = {
        'create': [NotAuthenticated],
        'retrieve': [permissions.IsAuthenticated],
        'update': [permissions.IsAuthenticated],
        'partial_update': [permissions.IsAuthenticated],
        'me': [permissions.AllowAny],
        'confirm_email': [permissions.AllowAny],
        'email_status': [permissions.AllowAny],
    }

    def get_object(self):
        return self.request.user

    def get_queryset(self):
        return self.model.objects.all()

    def get_serializer_class(self):
        return super(UsersViewSet, self).get_serializer_class()

    @list_route(methods=['GET'])
    def me(self, request, *args, **kwargs):
        try:
            data = self.get_serializer(request.user).data
            return Response(data, status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

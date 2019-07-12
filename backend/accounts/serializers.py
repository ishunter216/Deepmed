from rest_framework import serializers

import accounts.models


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()

    class Meta:
        model = accounts.models.User
        fields = ('id', 'email', 'first_name', 'last_name', 'password')
        extra_kwargs = {'id': {'read_only': True}}

    def create(self, validated_data):
        """
        Create the object.

        :param validated_data: string
        """
        user = accounts.models.User.objects.create(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user
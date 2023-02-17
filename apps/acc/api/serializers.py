from rest_framework import serializers

from project.contrib.drf.serializers import ModelSerializer
from acc import models as acc_models

__all__ = [
    'LoginSerializer',
    'WhoAmISerializer',
]


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=128)


class WhoAmISerializer(ModelSerializer):
    class Meta:
        model = acc_models.User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'is_superuser', 'is_staff', 'is_active',
        ]

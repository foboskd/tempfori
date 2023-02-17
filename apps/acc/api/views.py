from functools import partial

from django.conf import settings
from django.contrib.auth import login, authenticate, logout
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import generics, status, mixins, serializers
from rest_framework.response import Response
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from project.contrib.drf.serializers import StatusSerializer, EmptySerializer
from project.contrib.drf.permissions import AllowAny
from project.contrib.drf.openapi import openapi_response_guest, openapi_response_user
from acc.api import serializers as acc_serializers
from acc import models as acc_models

__all__ = [
    'LoginView',
    'LogoutView',
    'WhoAmIView',
    'PasswordChangeView',
]


class LoginView(generics.GenericAPIView):
    serializer_class = acc_serializers.LoginSerializer
    serializer_response_class = acc_serializers.WhoAmISerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: openapi.Response('If it is OK', serializer_response_class()),
            status.HTTP_401_UNAUTHORIZED: openapi.Response('If credentials is not OK', StatusSerializer()),
        }
    )
    def post(self, request, *args, **kwargs):
        request_serializer = self.get_serializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        if settings.DEBUG:
            user = acc_models.User.objects.filter(email=request_serializer.validated_data.get('email')).first()
        else:
            user = authenticate(
                request,
                username=request_serializer.validated_data.get('email'),
                password=request_serializer.validated_data.get('password')
            )
        if user:
            response_status = status.HTTP_200_OK
            login(request, user)
            response_serializer = self.serializer_response_class(instance=user, context={'request': request})
        else:
            response_data = {'status': 'error', 'details': 'Bad email or password'}
            response_status = status.HTTP_401_UNAUTHORIZED
            response_serializer = StatusSerializer(data=response_data)
            response_serializer.is_valid()
        return Response(response_serializer.data, status=response_status)


class LogoutView(generics.GenericAPIView):
    serializer_class = StatusSerializer

    @swagger_auto_schema(
        operation_description='It authorizes the user',
        request_body=EmptySerializer(),
        responses={
            status.HTTP_200_OK: openapi_response_guest(StatusSerializer()),
            status.HTTP_403_FORBIDDEN: openapi_response_user(StatusSerializer()),
        }
    )
    def post(self, request, *args, **kwargs):
        logout(request)
        response_serializer = StatusSerializer(data={'status': 'ok'})
        response_serializer.is_valid()
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class WhoAmIView(generics.RetrieveAPIView, mixins.UpdateModelMixin):
    """
    Данные о текущем пользователе
    """
    http_method_names = ['get']
    queryset = acc_models.User.objects.all()
    serializer_class = acc_serializers.WhoAmISerializer

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: openapi_response_guest(serializer_class()),
            status.HTTP_403_FORBIDDEN: openapi_response_user(StatusSerializer()),
        }
    )
    @transaction.atomic
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def get_object(self):
        return self.request.user


class PasswordChangeView(generics.GenericAPIView):
    class Serializer(serializers.Serializer):
        new_password = serializers.CharField(max_length=128)
        new_password_again = serializers.CharField(max_length=128)

        def validate(self, attrs):
            try:
                password_validation.validate_password(attrs['new_password'])
            except DjangoValidationError as e:
                raise serializers.ValidationError({'new_password': e.messages})
            if attrs['new_password'] != attrs['new_password_again']:
                raise serializers.ValidationError({'new_password_again': _('Пароли не совпадают')})
            return attrs

        def save(self):
            request = self.context['request']
            u = request.user
            u.set_password(self.validated_data['new_password'])
            u.save()
            login(request, u)
            return self.instance

    serializer_class = Serializer

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: StatusSerializer()
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            StatusSerializer({'status': 'ok', 'details': _('Пароль изменен')}).data,
            status=status.HTTP_200_OK
        )

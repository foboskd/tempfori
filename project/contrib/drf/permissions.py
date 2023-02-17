from typing import Optional

from rest_framework.permissions import (
    AllowAny as AllowAnyBase,
    IsAuthenticated as IsAuthenticatedBase,
    IsAuthenticatedOrReadOnly as IsAuthenticatedOrReadOnlyBase,
    DjangoModelPermissions,
)


class ModelObjectPermissions(DjangoModelPermissions):
    def has_permission(self, request, view):
        if not (fnc := getattr(self, f'object_has_action_permission__{view.action}', None)):
            fnc = super().has_permission
        return fnc(request, view)

    def object_has_action_permission__list(self, request, view) -> Optional[bool]:
        return IsAuthenticated().has_permission(request, view)

    def object_has_action_permission__retrieve(self, request, view):
        return self.object_has_action_permission__list(request, view)

    def object_has_action_permission__create(self, request, view) -> Optional[bool]:
        if hasattr(view.queryset.model.objects, 'has_add_permission'):
            return view.queryset.model.objects.has_add_permission(request.user)

    def object_has_action_permission__update(self, request, view) -> Optional[bool]:
        obj = view.get_object()
        if hasattr(obj, 'user_has_change_permission'):
            return obj.user_has_change_permission(request.user)

    def object_has_action_permission__partial_update(self, request, view) -> Optional[bool]:
        return self.object_has_action_permission__update(request, view)

    def object_has_action_permission__destroy(self, request, view) -> Optional[bool]:
        obj = view.get_object()
        if hasattr(obj, 'user_has_delete_permission'):
            return obj.user_has_delete_permission(request.user)

    def object_has_action_permission__delete_many(self, request, view) -> Optional[bool]:
        return IsAuthenticated().has_permission(request, view)


class AllowAny(AllowAnyBase):
    pass


class IsAuthenticatedOrReadOnly(IsAuthenticatedOrReadOnlyBase):
    pass


class IsAuthenticated(IsAuthenticatedBase):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class IsSuperUser(IsAuthenticated):
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser

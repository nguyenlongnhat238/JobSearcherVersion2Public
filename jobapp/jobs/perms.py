from rest_framework import permissions
from .models import User, UserProfile


class OwnerPerms(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        return request.user == obj.user


class EduAndExpPerms(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        profile = UserProfile.objects.filter(user=request.user).first()
        return profile.id == obj.user.id


class ProfilePerms(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        profile = UserProfile.objects.get(user=request.user)
        return obj.user == profile


class PostCreateHirerPerms(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        user = request.user
        if user.user_role is None:
            return False
        return user.user_role_id == 3


class OwnerPostPerms(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.user_role_id != 3:
            print(user)
            return False
        return obj.company.user == user


class RatingPerms(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.user_role_id == 3:
            return False
        return True

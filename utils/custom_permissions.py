from rest_framework import permissions

CUSTOM_MESSAGE = 'You do not have permission to do this action.'


class BlacklistPartialUpdateActionPermission(permissions.BasePermission):
    """
    Global permission check for blacklisted Partial Update action.
    """
    message = CUSTOM_MESSAGE

    def has_permission(self, request, view):
        return view.action != 'partial_update'

    def has_object_permission(self, request, view, obj):
        return view.action != 'partial_update'


class BlacklistUpdateActionPermission(permissions.BasePermission):
    """
    Global permission check for blacklisted UPDATE action.
    """
    message = CUSTOM_MESSAGE

    def has_permission(self, request, view):
        return view.action != 'update'

    def has_object_permission(self, request, view, obj):
        return view.action != 'update'


class BlacklistDestroyActionPermission(permissions.BasePermission):
    """
    Global permission check for blacklisted Destroy action.
    """
    message = CUSTOM_MESSAGE

    def has_permission(self, request, view):
        return view.action != 'destroy'

    def has_object_permission(self, request, view, obj):
        return view.action != 'destroy'


class BlacklistListActionPermission(permissions.BasePermission):
    """
    Global permission check for blacklisted List action.
    """
    message = CUSTOM_MESSAGE

    def has_permission(self, request, view):
        return view.action != 'list'


class BlacklistRetrieveActionPermission(permissions.BasePermission):
    """
    Global permission check for blacklisted Retrieve action.
    """
    message = CUSTOM_MESSAGE

    def has_permission(self, request, view):
        return view.action != 'retrieve'

    def has_object_permission(self, request, view, obj):
        return view.action != 'retrieve'


class BlacklistCreateActionPermission(permissions.BasePermission):
    """
    Global permission check for blacklisted Retrieve action.
    """
    message = CUSTOM_MESSAGE

    def has_permission(self, request, view):
        return view.action != 'create'

    def has_object_permission(self, request, view, obj):
        return view.action != 'create'

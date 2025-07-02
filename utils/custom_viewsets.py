from utils import custom_mixins
from rest_framework import viewsets


class ModelViewSet(custom_mixins.CreateModelMixin,
                   custom_mixins.RetrieveModelMixin,
                   custom_mixins.UpdateModelMixin,
                   custom_mixins.DestroyModelMixin,
                   custom_mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    """
    A viewset that provides default `create()`, `retrieve()`, `update()`,
    `partial_update()`, `destroy()` and `list()` actions.
    """
    pass


class ReadOnlyModelViewSet(custom_mixins.RetrieveModelMixin,
                           custom_mixins.ListModelMixin,
                           viewsets.GenericViewSet):
    """
    A viewset that provides default `list()` and `retrieve()` actions.
    """
    pass


class ListModelViewSet(custom_mixins.ListModelMixin,
                       viewsets.GenericViewSet):
    """
    A viewset that provides default `list()` actions.
    """
    pass


class UpdateModelViewSet(custom_mixins.UpdateModelMixin,
                         viewsets.GenericViewSet):
    """
    A viewset that provides default`update()`,
    `partial_update()` actions.
    """
    pass


class CreateModelViewSet(custom_mixins.CreateModelMixin,
                    viewsets.GenericViewSet):
    """
    A viewset that provides default `create()`, `retrieve()`, `update()`,
    `partial_update()`, `destroy()` and `list()` actions.
    """
    pass

"""
Basic building blocks for generic class based views.

We don't bind behaviour to http method handlers yet,
which allows mixin classes to be composed in interesting ways.
"""
from rest_framework import status
from rest_framework.response import Response
from rest_framework.settings import api_settings


class CreateModelMixin:
    """
    Create a model instance.
    """

    def create(self, request, *args, **kwargs):
        many_objects_supported = request.query_params.get(
            'post_many', None) == 'True'
        serializer = self.get_serializer(data=request.data, context={
                                         'request': request}, many=many_objects_supported)
        serializer.is_valid(raise_exception=True)

        obj = self.perform_create(serializer)
        list_serializer = self.serializer_class(obj)
        headers = self.get_success_headers(list_serializer.data)

        data = {
            "data": list_serializer.data,
            "message": self.create_success_message
        }
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        return serializer.save()

    def get_success_headers(self, data):
        try:
            return {'Location': str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}


class ListModelMixin:
    """
    List a queryset.
    """

    def list(self, request, *args, **kwargs):
        pagination_data = None

        queryset = self.filter_queryset(self.get_queryset())

        if hasattr(queryset, 'distinct'):
            queryset = queryset.distinct()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, context={
                'request': request}, many=True)
            pagination_data = self.get_paginated_response(None)
        else:
            serializer = self.get_serializer(queryset, context={
                'request': request}, many=True)

        data = {
            "status_code": self.status_code,
            "data": serializer.data,
            "message": self.list_success_message,
        }
        if hasattr(self, 'extra_data') is True:
            data["extra_data"] = self.extra_data

        if pagination_data:
            data["pagination_data"] = pagination_data

        return Response(data, status=status.HTTP_200_OK)



class RetrieveModelMixin:
    """
    Retrieve a model instance.
    """

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = {
            "data": serializer.data,
            "message": self.retrieve_success_message
        }
        return Response(data, status=status.HTTP_200_OK)


class UpdateModelMixin:
    """
    Update a model instance.
    """

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        data = {
            "data": self.serializer_class(self.get_object()).data,
            "message": self.update_success_message
        }
        return Response(data, status=status.HTTP_200_OK)

    def perform_update(self, serializer):
        return serializer.save()

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)


class DestroyModelMixin:
    """
    Destroy a model instance.
    """

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        data = {
            "message": self.delete_success_message,
        }
        return Response(data, status=status.HTTP_200_OK)

    def perform_destroy(self, instance):
        instance.delete()

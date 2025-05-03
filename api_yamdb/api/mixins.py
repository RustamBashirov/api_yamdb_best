from rest_framework import viewsets, mixins, status
from rest_framework.response import Response


class PartialUpdateModelMixin(mixins.UpdateModelMixin):
    """
    Миксин для обработки только PATCH (без PUT) запросов.
    """

    def update(self, request, *args, **kwargs):
        if request.method == 'PUT':
            return Response(
                {'detail': 'Метод PUT не разрешен.'},
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )
        return super().update(request, *args, **kwargs)


class ListCreateDestroyMixin(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    pass


class RetrieveListCreatePartialUpdateDestroyMixin(
    PartialUpdateModelMixin,
    mixins.RetrieveModelMixin,
    ListCreateDestroyMixin
):
    pass

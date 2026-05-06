from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from menu.models import Item
from .serializers import InventoryItemSerializer


class InventoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for inventory management.

    GET  /api/inventory/          → list all items with availability status
    GET  /api/inventory/?available=true  → list only available items
    GET  /api/inventory/<id>/     → single item detail
    PATCH /api/inventory/<id>/    → update is_available only
    POST /api/inventory/<id>/toggle/ → toggle availability on/off
    """
    queryset = Item.objects.all().order_by('category', 'name')
    serializer_class = InventoryItemSerializer
    permission_classes = [IsAdminUser]
    http_method_names = ['get', 'patch', 'post', 'head', 'options']
    # Disallow DELETE and PUT from this API surface

    def get_queryset(self):
        qs = super().get_queryset()
        available = self.request.query_params.get('available')
        if available is not None:
            qs = qs.filter(is_available=(available.lower() == 'true'))
        return qs

    @action(detail=True, methods=['post'], url_path='toggle')
    def toggle_availability(self, request, pk=None):
        """
        Convenience endpoint: flips is_available without sending a body.
        POST /api/inventory/<id>/toggle/
        """
        item = self.get_object()
        item.is_available = not item.is_available
        item.save(update_fields=['is_available'])
        return Response(
            {'id': item.id, 'name': item.name, 'is_available': item.is_available},
            status=status.HTTP_200_OK
        )

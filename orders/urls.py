from django.urls import path
from . import views


urlpatterns = [
    path('order/', views.create_order, name='create_order'),
    path('order/<int:table_order_id>/', views.delete_order, name='delete_order'),
    path('order/<int:table_order_id>/', views.complete_order, name='complete_order'),
]
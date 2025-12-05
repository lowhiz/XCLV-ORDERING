from django.urls import path
from . import views


urlpatterns = [
    path('order/', views.create_order, name='create_order'),
    path('order_details/<int:order_id>/', views.past_order_details, name='order_details'),
    path('order-success/', views.order_success, name='order_success'),
    path('order/delete/<int:table_order_id>/', views.delete_order, name='delete_order'),
    path('order/complete/<int:table_order_id>/', views.complete_order, name='complete_order'),
    path('update-order/', views.update_order, name='update_order'),
    path('review-order/<int:table_id>/', views.review_order, name='review_order'),
]

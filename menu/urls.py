from django.urls import path
from . import views


urlpatterns = [
    path('view/', views.view_menu, name='view_menu'),
    path('review/', views.review, name='review'),
    path('close_menu/', views.close_menu, name='close_menu'),
    path('open_menu/', views.open_menu, name='open_menu'),
    path('admin_toggle_menu/', views.admin_toggle_menu, name='admin_toggle_menu'),
    path('check_menu_status/', views.check_menu_status, name='check_menu_status'),
    # Feature armed from the DRF inventory app to allow admins to toggle item availability from the admin menu page
    path('toggle-availability/<int:item_id>/', views.toggle_item_availability, name='toggle_item_availability'),
    path('add-product/', views.admin_add_product, name='admin_add_product'),
    path('admin-edit-product/<int:item_id>/',views.admin_edit_product,name='admin_edit_product'),
    path('admin-delete-product/<int:item_id>/',views.admin_delete_product,name='admin_delete_product'),
]

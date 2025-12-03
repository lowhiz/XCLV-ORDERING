from django.urls import path
from . import views

urlpatterns = [
    # Route for archiving a specific table and deleting its active records
    # <int:table_id> dynamically captures the table's ID from the URL
    path('table/<int:table_id>/archive/', views.archive_and_delete_table, name='archive_table'),
    
    # Route for displaying all archived table records
    path('archives/', views.show_archive_data, name='show_archive_data'),
    path('archives/<str:table_name>/', views.archive_details, name='archive_details'),
]

from django.urls import path
from . import views

urlpatterns = [
    # This loads the login page and handles form submission
    path("", views.admin_login, name="admin_login"),
]

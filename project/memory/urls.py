from django.urls import path
from .views import \
    get_welcome, create_memory, list_memory, edit_memory, delete_memory

urlpatterns = [
    path("create/", create_memory, name="create_memory"),
    path("list/", list_memory, name="list_memory"),
    path("edit/<str:memory_id>/", edit_memory, name="edit_memory"),
    path("delete/<str:memory_id>/", delete_memory, name="delete_memory"),
    path("", get_welcome, name="welcome_page"),
]

from django.urls import path
from .views import (
    UserListView,
    CreateClientView,
    CreateContractorView,
    UserDetailView,
)

urlpatterns = [
    path('',                    UserListView.as_view()),           # GET all users
    path('create-client/',      CreateClientView.as_view()),       # POST create client
    path('create-contractor/',  CreateContractorView.as_view()),   # POST create contractor
    path('<int:pk>/',           UserDetailView.as_view()),         # GET/PUT/DELETE user
]
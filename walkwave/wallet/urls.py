from django.urls import path
from . import views

urlpatterns = [
    path('view_wallet/', views.view_wallet, name='view_wallet'),
]
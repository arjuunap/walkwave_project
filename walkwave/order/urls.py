from django.urls import path
from . import views

urlpatterns = [
    path('admin/orders/', views.admin_order_list, name='admin_order_list'),
    path('admin/orders/<int:order_id>/change-status/', views.admin_change_order_status, name='admin_change_order_status'),
    path('admin/orders/<int:order_id>/cancel/', views.admin_cancel_order, name='admin_cancel_order'),
]
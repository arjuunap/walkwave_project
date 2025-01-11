from django.urls import path
from . import views


urlpatterns = [
    path('coupon_management/',views.coupon_management,name='coupon_management'),
    path('add_coupon', views.add_coupon, name='add_coupon'),
    path('admin/coupon/delete/<int:coupon_id>/', views.delete_coupon, name='delete_coupon'),
    path('apply-coupon/', views.apply_coupon, name='apply_coupon'),

]

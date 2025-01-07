from django.urls import path
from . import views


app_name='user'


urlpatterns = [
    path('user_profile/', views.user_profile, name='user_profile'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('user_address',views.user_address,name='user_address'),
    path('add_address',views.add_address,name='add_address'),
    path('set-default/<int:id>/', views.set_default_address, name='set_default_address'),
    path('delete/<int:id>/', views.delete_address, name='delete_address'),
    path('edit_address/<int:id>/',views.edit_address,name='edit_address'),
    path('change_password/', views.change_password, name='change_password'),
    path('forgot_password',views.forgot_password,name='forgot_password'),
    path('reset_password',views.reset_password,name='reset_password'),
    path("add_or_edit_address/", views.add_or_edit_address, name="add_or_edit_address"),

]
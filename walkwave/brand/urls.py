from django.urls import path
from . import views

app_name='brand'

urlpatterns = [
    path('brand_list/',views.brand_list,name='brand_list'),
    path('add_brand/',views.add_brand,name='add_brand'),
    path('block_brand/<int:id>/',views.block_brand,name='block_brand'),
    path('unblock_brand/<int:id>/',views.unblock_brand,name='unblock_brand'),
    path('soft_delete_brand/<int:id>/',views.soft_delete_brand,name='soft_delete_brand'),
    path('edit_brand/<int:id>/',views.edit_brand,name='edit_brand')
    
]

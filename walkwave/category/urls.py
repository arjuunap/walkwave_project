from django.urls import path
from . import views

app_name='category'


urlpatterns = [
    path('category_list',views.category_list,name='category_list'),
    path('add_category',views.add_category,name='add_category'),
    path('block_category/<int:id>/',views.block_category,name='block_category'),
    path('unblock_category/<int:id>/',views.unblock_category,name='unblock_category'),
    path('category_soft_delete/<int:id>/',views.category_soft_delete,name='category_soft_delete'),
    path('edit_category/<int:id>/',views.edit_category,name='edit_category')
    
]

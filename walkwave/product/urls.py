from django.urls import path
from . import views


app_name='product'


urlpatterns = [
    path('product_list',views.product_list,name='product_list'),
    path('add_product',views.add_product,name='add_product'),
    path('edit_product/<int:id>/',views.edit_product,name='edit_product'),
    path('edit_product_images/<int:id>/',views.edit_product_images,name='edit_product_images'),
    path('add_image_for_product/<int:id>/',views.add_images_for_product,name='add_images_for_product'),
    path('product_detail/<int:id>/',views.product_detail,name='product_detail'),
    path('admin_side_product_detail/<int:id>/',views.admin_side_product_detail,name='admin_side_product_detail'),
    path('product_status/<int:id>/',views.product_status,name='product_status'),
    path('product_soft_delete/<int:id>/',views.product_soft_delete,name='product_soft_delete'),
    path('product_variants_list/<int:id>/',views.product_variant_list,name='product_variants_list'),
    path('product_shop',views.product_shop,name='product_shop')
]

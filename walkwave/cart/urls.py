from django.urls  import path
from . import views



urlpatterns = [
    path('cart_page/',views.cart_page,name='cart_page'),
    path('add-to-cart/', views.add_to_cart, name='add-to-cart'),
    path('cart_remove_item/<int:item_id>/',views.cart_remove_item, name='cart_remove_item'),
    path('update-cart-quantity/', views.update_cart_quantity, name='update_cart_quantity'),
    path('checkout_page',views.checkout_page,name='checkout_page'),
    path('order_confirmed/<int:id>/', views.order_confirmed, name='order_confirmed'),
    path('user_orders',views.user_orders,name='user_orders')
]
    
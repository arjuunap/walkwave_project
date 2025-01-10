from django.urls  import path
from . import views



urlpatterns = [
    path('cart_page/',views.cart_page,name='cart_page'),
    path('add-to-cart/', views.add_to_cart, name='add-to-cart'),
    path('cart_remove_item/<int:item_id>/',views.cart_remove_item, name='cart_remove_item'),
    path('update-cart-quantity/', views.update_cart_quantity, name='update_cart_quantity'),
    path('checkout_page',views.checkout_page,name='checkout_page'),
    path('order_confirmed/<int:id>/', views.order_confirmed, name='order_confirmed'),
    path('user_orders',views.user_orders,name='user_orders'),
    path('cancel_order/<int:id>/',views.cancel_order,name='cancel_order'),
    path('order_details/<int:id>/',views.order_details,name='order_details'),
    path('return_order/<int:id>/',views.return_order,name='return_order'),
    path('payment/success/', views.razorpay_payment_success, name='razorpay_payment_success'),



]
    
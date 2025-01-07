from django.shortcuts import render,redirect
from django.contrib import messages
from user.models import Address

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import Cart, CartItem
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from product.models import Product, ProductVariant
import json
from order.models import Order, OrderItem, PaymentMethod
from django.db import transaction

# Create your views here.


def cart_page(request):
    cart = Cart.objects.filter(user=request.user).first()  
    cart_items = cart.items.select_related('product', 'variant') if cart else []

    context = {
        'cart': cart,
        'cart_items': cart_items,
    }
    return render(request, 'user_side/shoping-cart.html', context)


@csrf_exempt
@login_required
def add_to_cart(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            variant_id = data.get('variant_id')
            quantity = int(data.get('quantity', 1))

            if quantity < 1:
                quantity = 1

            variant = get_object_or_404(ProductVariant, id=variant_id)

            if variant.variant_stock < quantity:
                return JsonResponse({'success': False, 'message': 'Not enough stock available.'}, status=400)

            with transaction.atomic():
                cart, created = Cart.objects.get_or_create(user=request.user)

                cart_item, created = CartItem.objects.get_or_create(
                    cart=cart,
                    product=variant.product,
                    variant=variant,
                    defaults={
                        'quantity': 0,
                        'price': variant.product.offer_price or variant.product.price,
                    }
                )

                if not created:
                    cart_item.quantity += quantity
                else:
                    cart_item.quantity = max(1, quantity)

                if cart_item.quantity > variant.variant_stock:
                    return JsonResponse({'success': False, 'message': 'Quantity exceeds available stock.'}, status=400)

                if created:
                    variant.variant_stock -= cart_item.quantity
                else:
                    variant.variant_stock -= quantity

                variant.save()
                cart_item.save()

                cart.total_price = cart.calculate_total_price()
                cart.save()

            return JsonResponse({'success': True, 'message': 'Item added to cart.', 'cart_count': cart.items.count()})

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON data.'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)

    return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=405)


@login_required
def cart_remove_item(request, item_id):
    if request.method == "POST":
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        print(f' thi {cart_item}')

        try:
            with transaction.atomic():
                if cart_item.variant:
                    cart_item.variant.variant_stock += cart_item.quantity
                    cart_item.variant.save()

                cart_item.delete()

                messages.success(request, "Item removed from the cart successfully.")
        except Exception :
            messages.error(request, "Error")

        return redirect('cart_page')
    messages.error(request, "Invalid request method.")
    return redirect('cart_page')

    




from decimal import Decimal
def update_cart_quantity(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        item_id = data.get('item_id')
        new_quantity = data.get('quantity')

        try:
            cart_item = CartItem.objects.get(id=item_id)
            current_quantity = cart_item.quantity

            variant = cart_item.variant

            if new_quantity > current_quantity:
                quantity_increase = new_quantity - current_quantity

                if variant and variant.variant_stock < quantity_increase:
                    return JsonResponse({
                        'success': False,
                        'message': f'Only {variant.variant_stock} items available in stock.'
                    }, status=400)

                if variant:
                    variant.variant_stock -= quantity_increase
                    variant.save()

                    if variant.variant_stock == 0:
                        variant.variant_status = False
                        variant.save()

            elif new_quantity < current_quantity:
                quantity_decrease = current_quantity - new_quantity

                if variant:
                    variant.variant_stock += quantity_decrease
                    variant.variant_status = True  
                    variant.save()

            if variant and new_quantity > variant.variant_stock + current_quantity:
                return JsonResponse({
                    'success': False,
                    'message': f'Stock not available. Maximum {variant.variant_stock + current_quantity} can be added.'
                }, status=400)

            cart_item.quantity = new_quantity
            cart_item.save()

            total_price = cart_item.total_price()

            cart = cart_item.cart

            cart_total_price = Decimal(0.00)
            total_items = 0
            for item in cart.items.all():
                cart_total_price += item.total_price()
                total_items += item.quantity

            if cart.delivery_charge:
                cart_total_price += Decimal(cart.delivery_charge)

            return JsonResponse({
                'success': True,
                'item_total_price': str(total_price),
                'cart_total_price': str(cart_total_price),
                'total_items': total_items,
                'available_stock': variant.variant_stock if variant else None
            })

        except CartItem.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Cart item not found.'
            }, status=404)

    return JsonResponse({
        'success': False,
        'message': 'Invalid request method.'
    }, status=400)




from django.shortcuts import get_object_or_404
import logging

# Set up logging
logger = logging.getLogger(__name__)

@login_required
def checkout_page(request):
    
    addresses = Address.objects.filter(user=request.user)

    cart = Cart.objects.filter(user=request.user).first()
   

    if not cart or not cart.items.exists():
        messages.error(request, "Your cart is empty. Please add items to proceed to checkout.")
        return redirect('cart_page')

    payment_methods = [
        {"method": "COD", "display": "Cash on Delivery"},
        {"method": "Online", "display": "Online Payment"},
        {"method": "Wallet", "display": "Wallet Payment"},
    ]

    if request.method == "POST":
        address_id = request.POST.get('address_id')
        payment_method = request.POST.get('payment_method')

        if not address_id:
            messages.error(request, "Please select a delivery address.")
            return redirect('checkout_page')

       
        address = get_object_or_404(Address, id=address_id, user=request.user)
        print(f"Selected address: {address}")

        try:
            
            order = Order(
                user=request.user,
                address=address,
                total_price=cart.calculate_total_price(),
                delivery_charge=cart.delivery_charge or 0.00,
                status='Pending',
            )
            order.save()

            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    variant=item.variant,
                    quantity=item.quantity,
                    price=item.price,
                    discount=item.discount,
                )

            PaymentMethod.objects.create(
                user=request.user,
                method=payment_method,
            )

            cart.delete()

            messages.success(request, "Your order has been placed successfully.")
            return redirect('order_confirmed', id=order.id)

        except Exception :
            messages.error(request, "An error occurred while processing your order. Please try again.")
            return redirect('checkout_page')

    total_amount = cart.calculate_total_price()
    total_discount = sum(item.discount for item in cart.items.all())
    return render(request, 'user_side/checkout.html', {
        'addresses': addresses,
        'cart': cart,
        'payment_methods': payment_methods,
        'total_amount': total_amount,
        'total_discount': total_discount,
    })


@login_required
def order_confirmed(request, id):
    order = get_object_or_404(Order, id=id, user=request.user)
    return render(request, 'user_side/order_confirm.html', {'order': order})


def user_orders(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items__product', 'address')
    print(orders) 
    return render(request, 'user_side/user_orders.html', {
        'orders': orders,
    })


@login_required
def cancel_order(request,id):
    order = get_object_or_404( Order , id=id , user= request.user)

    if order .status not in ['Cancelled' , 'Delivered']:
        order.status = 'Cancelled'
        order.save()
        messages.success(request , 'Your order had been canceled successfully canceled')
    else:
        messages.warning(request, 'this orderc cannot be canceled')
    
    return redirect('user_orders')


@login_required
def order_details(request,id):
    order = get_object_or_404(Order, id =id ,user =request.user)
    payment_method = PaymentMethod.objects.filter(user=request.user).first()
    return render (request, 'user_side/order_details.html',{'order':order, 'payment_method': payment_method})



    


from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Coupon
from cart.models import Cart,CartItem
from account_app.models import User



def add_coupon(request):
    if request.method == 'POST':
        # Get data from the form
        name = request.POST.get('name')
        discount = request.POST.get('discount')
        minimum_price = request.POST.get('minimum_price')
        expiry_date = request.POST.get('expiry_date')
        count = request.POST.get('count')

        
        if not (name and discount and minimum_price and expiry_date and count):
            messages.error(request, 'All fields are required.')
            return redirect('add_coupon')

        
        try:
            discount = float(discount)
            minimum_price = float(minimum_price)
            count = int(count)

            if discount <= 0 or minimum_price <= 0 or count <= 0:
                messages.error(request, 'Discount, minimum price, and count must be greater than zero.')
                return redirect('add_coupon')
        except ValueError:
            messages.error(request, 'Invalid values for discount, minimum price, or count.')
            return redirect('add_coupon')

        
        from datetime import datetime
        try:
            expiry_date_obj = datetime.strptime(expiry_date, '%Y-%m-%d').date()
            if expiry_date_obj <= datetime.now().date():
                messages.error(request, 'Expiry date must be a future date.')
                return redirect('add_coupon')
        except ValueError:
            messages.error(request, 'Invalid expiry date format. Please use YYYY-MM-DD.')
            return redirect('add_coupon')

        
        Coupon.objects.create(
            name=name,
            discount=discount,
            minimum_price=minimum_price,
            expiry_date=expiry_date,
            count=count
        )

        messages.success(request, 'Coupon added successfully!')
        return redirect('coupon_management')

    
    return render(request, 'admin_side/add_coupon.html')



def coupon_management(request):
   
    coupons = Coupon.objects.all()  
    context = {
        'coupons': coupons,
    }
    return render(request, 'admin_side/coupon.html', context)


def delete_coupon(request, coupon_id):
    if request.method == 'POST':
        coupon = get_object_or_404(Coupon, id=coupon_id)
        
        coupon.delete()
        
        return JsonResponse({'status': 'success'})
    
    return JsonResponse({'status': 'error'}, status=400)

import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404


def apply_coupon(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            coupon_id = data.get('coupon_id')

            coupon = get_object_or_404(Coupon, id=coupon_id, active=True)
            cart = Cart.objects.filter(user=request.user).first()

            if not cart:
                return JsonResponse({'success': False, 'message': 'Cart not found.'})

            total_price = cart.calculate_total_price()

            if total_price < coupon.minimum_price:
                return JsonResponse({
                    'success': False,
                    'message': f'Minimum price for this coupon is ₹{coupon.minimum_price}.',
                    'total_price': float(total_price),
                    'after_discount': float(total_price),
                    'discount_amount': 0,
                })

            if coupon.count <= 0:
                return JsonResponse({'success': False, 'message': 'Coupon usage limit exceeded.'})

            discount = coupon.discount 
            after_discount = total_price - discount
            print(after_discount)

            request.session['applied_coupon'] = coupon.id

            return JsonResponse({
                'success': True,
                'message': f'Coupon "{coupon.name}" applied successfully.',
                'total_price': float(total_price),
                'after_discount': float(after_discount),
                'discount_amount': float(discount),
            })

        except Coupon.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid coupon.'})
        

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

from django.shortcuts import redirect, get_object_or_404,render
from django.contrib import messages
from . models import Wishlist
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from product.models import Product
import json



def wishlist_view(request):
    wishlist_items = Wishlist.objects.filter(user=request.user)
    return render(request, 'user_side/wishlist.html', {'wishlist_items': wishlist_items})


@csrf_exempt
def add_to_wishlist(request):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'User is not authenticated.'}, status=401)
    
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = data.get('product_id')
        product = Product.objects.filter(id=product_id).first()
        
        if product:
            created = Wishlist.objects.get_or_create(user=request.user, product=product)
            if created:
                return JsonResponse({'success': True, 'message': 'Product added to wishlist!'})
            else:
                return JsonResponse({'success': False, 'message': 'Product is already in your wishlist!'})
        else:
            return JsonResponse({'success': False, 'message': 'Invalid product.'})
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})



def remove_from_wishlist(request, wishlist_id):
    if request.method == 'GET':
        wishlist_item = get_object_or_404(Wishlist, id=wishlist_id, user=request.user)
        wishlist_item.delete()
        return redirect('wishlist') 
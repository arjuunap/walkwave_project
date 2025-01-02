from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from .models import Order
# Create your views here.


def admin_order_list(request):
   
    orders = Order.objects.all().order_by('-ordered_at')
    return render(request, 'admin_side/order_details.html', {'orders': orders})

def admin_change_order_status(request, order_id):
    
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        new_status = request.POST.get('status')
        if new_status in dict(Order.status_choices):
            order.status = new_status
            order.save()
            messages.success(request, f"Order {order.order_id} status updated to {new_status}.")
        else:
            messages.error(request, "Invalid status selected.")
        return redirect('admin_order_list')


def admin_cancel_order(request, order_id): 
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        order.status = 'Cancelled'
        order.save()
        messages.success(request, f"Order {order.order_id} has been cancelled.")
        return redirect('admin_order_list')
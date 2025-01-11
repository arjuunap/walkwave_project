from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Order
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# Create your views here.


def admin_order_list(request):
    orders_list = Order.objects.all().order_by('-ordered_at')
    
    # Number of orders per page
    per_page = 10
    paginator = Paginator(orders_list, per_page)
    
    page = request.GET.get('page')
    try:
        orders = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        orders = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page of results.
        orders = paginator.page(paginator.num_pages)
    
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
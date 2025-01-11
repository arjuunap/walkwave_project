from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from account_app.models import User
from django.views.decorators.cache import cache_control
from django.contrib.auth.decorators import login_required
from utils.decorators import admin_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Create your views here.


def admin_login(request):

    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_dashboard')

    if request.method=='POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user=authenticate(request,username=email,password=password)

        if user is not None:
            if user.is_superuser:
                login(request,user)
                return redirect('admin_dashboard')
            else:
                messages.error(request,'you have not have permission to access admin panel')
        else:
            messages.error(request,'Invalid email or password')

    return render(request,'admin_side/admin_login.html')


@admin_required
@cache_control(no_cache=True, no_store=True, must_revalidate=True)
@login_required
def admin_dashboard(request):
    print('user:',request.user)
    return render(request,'admin_side/admin_dashboard.html')




def admin_logout(request):
    logout(request)
    messages.success(request,'logout sucessfully')
    return redirect('admin_login')



@admin_required
@cache_control(no_cache=True, no_store=True, must_revalidate=True)
@login_required
def user_listing(request):
    users_list = User.objects.filter(is_staff=False).order_by('id')
    
    # Number of users per page
    per_page = 10
    paginator = Paginator(users_list, per_page)
    
    page = request.GET.get('page')
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        users = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page of results.
        users = paginator.page(paginator.num_pages)
    
    return render(request, 'admin_side/user_listing.html', {'users': users})



@admin_required
@cache_control(no_cache=True, no_store=True, must_revalidate=True)
@login_required
def user_status(request,user_id):
    if request.method == 'POST':          
        user=User.objects.get(id=user_id)
        user.is_active= not user.is_active
        user.save()
    return redirect('user_listing')
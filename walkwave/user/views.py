from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from account_app.models import User
from .models import Address
import re
from django.views.decorators.cache import cache_control
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth import logout
from django.contrib.auth import update_session_auth_hash
from account_app.views import generate_otp
from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail
from datetime import timedelta



@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def user_profile(request):
    context = {
        'user': request.user,
    }
    return render(request, 'user_side/user_profile.html', context)



@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_profile(request):
    if request.method=='POST':
        user_id = request.user.id
        if not user_id:
            messages.error(request, 'Session expired. Please log in again.')
            return redirect('login')
        
        username = request.POST.get('username')

        if not re.match(r"^[A-Za-z]{3,}(?: [A-Za-z]+)*$", username):
            messages.error(request, 'Invalid username, please enter a valid input.')
            return redirect('user:edit_profile')

        
        try:
            user_data = User.objects.get(id=user_id)
            user_data.username =  username

            user_data.save()
            messages.success(request, 'Profile updated.')
        except User.DoesNotExist:
            messages.error(request, 'User not found.')
        return redirect('user:user_profile')
        
    return render(request, 'user_side/edit_profile.html')





@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def user_address(request):
    user_addresses = Address.objects.filter(user=request.user)
    return render(request, 'user_side/address_manage.html', {'addresses': user_addresses})



@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_address(request):
    if request.method == 'POST':
        user = request.user
        form_data = request.POST

        
        label = form_data.get('label', '').strip()
        mobile_no = form_data.get('mobile_no', '').strip()
        pin_code = form_data.get('pin_code', '').strip()
        state = form_data.get('state', '').strip()
        address = form_data.get('address', '').strip()
        city = form_data.get('city', '').strip()
        default_address = form_data.get('default_address') == 'on'

        errors = {}

        if not label or label not in ['home', 'work', 'other']:
           errors['label'] = 'Please select a valid label (Home, Work, Other).'

        if not mobile_no or not re.match(r"^[6-9]\d{9}$", mobile_no):
            errors['mobile_no'] = 'Invalid mobile number. It must start with 6-9 and be 10 digits long.'
        
        if not pin_code or not re.match(r"^\d{6}$", pin_code):
            errors['pin_code'] = 'Invalid PIN code. It must be exactly 6 digits.'

        if not state:
            errors['state'] = 'State is required.'
        
        if not address:
            errors['address'] = 'Address is required.'

        if not city:
            errors['city'] = 'City is required.'

        if errors:
            return render(request, 'user_side/add_address.html', {
                'form_data': form_data,
                'errors': errors
            })

       
        Address.objects.create(
            user=user,
            label=label,
            phone_number=mobile_no,
            pin_code=pin_code,
            state=state,
            address=address,
            city=city,
            default_address=default_address
        )

        messages.success(request, 'Address added successfully.')
        return redirect('user:user_address')  

    return render(request, 'user_side/add_address.html')





@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def set_default_address(request, id):
    Address.objects.filter(user=request.user, default_address=True).update(default_address=False)
    address = get_object_or_404(Address, id=id, user=request.user)
    address.default_address = True
    address.save()

    messages.success(request, "Default address updated.")
    return redirect('user:user_address')  



@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def delete_address(request, id):
    address = get_object_or_404(Address, id=id, user=request.user)   
    if address.default_address:
        messages.error(request, "Cannot delete the default address. Set another address as default first.")
        return redirect('user:user_address')

    address.delete()
    messages.success(request, "Address removed successfully.")
    return redirect('user:user_address')  




def edit_address(request, id):
    address = get_object_or_404(Address, id=id, user=request.user)

    if request.method == 'POST':
        form_data = request.POST

        label = form_data.get('label', '').strip()
        mobile_no = form_data.get('mobile_no', '').strip()
        pin_code = form_data.get('pin_code', '').strip()
        state = form_data.get('state', '').strip()
        address_text = form_data.get('address', '').strip()
        city = form_data.get('city', '').strip()
        default_address = form_data.get('default_address') == 'on'

        errors = {}

        if not label or label not in ['home', 'work', 'other']:
            errors['label'] = 'Please select a valid label (Home, Work, Other).'

        if not mobile_no or not re.match(r"^[6-9]\d{9}$", mobile_no):
            errors['mobile_no'] = 'Invalid mobile number. It must start with 6-9 and be 10 digits long.'

        if not pin_code or not re.match(r"^\d{6}$", pin_code):
            errors['pin_code'] = 'Invalid PIN code. It must be exactly 6 digits.'

        if not state:
            errors['state'] = 'State is required.'

        if not address_text:
            errors['address'] = 'Address is required.'

        if not city:
            errors['city'] = 'City is required.'

        if errors:
            return render(request, 'user_side/edit_address.html', {
                'form_data': form_data,
                'errors': errors,
                'address': address
            })

        address.label = label
        address.phone_number = mobile_no
        address.pin_code = pin_code
        address.state = state
        address.address = address_text
        address.city = city

        if default_address:
            Address.objects.filter(user=request.user).update(default_address=False)
        address.default_address = default_address

        address.save()

        messages.success(request, 'Address updated successfully.')
        return redirect('user:user_address')


    return render(request, 'user_side/edit_address.html', {
        'address': address,
        'form_data': {
            'label': address.label,
            'mobile_no': address.phone_number,
            'pin_code': address.pin_code,
            'state': address.state,
            'address': address.address,
            'city': address.city,
            'default_address': address.default_address
        }
    })




@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def change_password(request):
    if request.method == 'POST':
        user_id = request.user.id
        if not user_id:
            logout(request)
            messages.error(request, 'An error has occurred. Please log in again.')
            return redirect('login')
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        try:
            user = User.objects.get(id=user_id)

            if not old_password:
                messages.error(request, 'Old password cannot be blank.')
                return redirect('user:change_password')
            
            if not check_password(old_password, user.password):
                messages.error(request, 'The old password is incorrect, please try again.')
                return redirect('user:change_password')
            
            if len(new_password) < 8 or " " in new_password:
                messages.error(request, 'Password must be at least 8 characters and cannot contain spaces.')
                return redirect('user:change_password')
            
            if new_password != confirm_password:
                messages.error(request, 'The new passwords do not match.')
                return redirect('user:change_password')

            if check_password(new_password, user.password):
                messages.error(request, 'New password cannot be the old one.')
                return redirect('user:change_password')

            user.password = make_password(new_password)
            user.save()

            update_session_auth_hash(request, user)

            messages.success(request, 'Your password has been successfully changed.')
            return redirect('user:user_profile')

        except User.DoesNotExist:
            messages.error(request, 'User not found.')
            return redirect('login')

    return render(request, 'user_side/change_password.html')




def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email = email)
            otp = generate_otp()
            otp_expiry = (timezone.now() + timedelta(minutes=5)).isoformat()

            send_mail(               
                        'Reset Your Password - Walkwave',

                        f'Your OTP is: {otp}',
                        settings.DEFAULT_FROM_EMAIL, 
                        [email], 
                    )
            request.session['user_data'] = {
                'user_id':user.id,
                'email': user.email,
                'otp':otp,
                'otp_expiry':otp_expiry,
            }
            messages.success(request, 'Please check your email for the verification code.')
            return redirect('user:reset_password')
        except User.DoesNotExist:
            messages.error(request, 'No account found with this email address.')

    return render(request,'user_side/forgot_password.html')



def reset_password(request):
    if request.method == 'POST':
        otp = request.POST.get('otp')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        
        user_data = request.session.get('user_data')
        if not user_data:
            messages.error(request, "Session expired or invalid. Please try again.")
            return redirect('user:forgot_password')
        
        if not otp or not new_password or not confirm_password:
            messages.error(request, "All fields are required. Please fill out the form completely.")
            return redirect('user:reset_password')

        if otp != user_data['otp']:
            messages.error(request, "Invalid OTP. Please try again.")
            return redirect('user:reset_password')

        
        otp_expiry = timezone.datetime.fromisoformat(user_data['otp_expiry'])
        if timezone.now() > otp_expiry:
            messages.error(request, "OTP has expired. Please request a new one.")
            return redirect('user:forgot_password')

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('user:reset_password')

        try:
            user = User.objects.get(id=user_data['user_id'])
            user.password = make_password(new_password) 
            user.save()

            del request.session['user_data']
            messages.success(request, "Your password has been reset successfully. Please log in.")
            return redirect('login')
        except User.DoesNotExist:
            messages.error(request, "User not found.")
            return redirect('user:forgot_password')

    return render(request, 'user_side/password_reset_page.html')
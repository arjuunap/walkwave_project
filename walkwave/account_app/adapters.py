from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.utils.timezone import now
from django.contrib.auth import get_user_model
from django.shortcuts import redirect

User = get_user_model()

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        """
        Handle existing users to authenticate and redirect without saving.
        """
        email = sociallogin.account.extra_data.get('email')
        if not email:
            return  

        try:
            existing_user = User.objects.get(email=email)
            
            sociallogin.connect(request, existing_user)
            return redirect('/')  
        except User.DoesNotExist:
            pass

    def save_user(self, request, sociallogin, form=None):
        """
        Save new user details into the custom User model.
        """
        data = sociallogin.account.extra_data
        email = data.get('email', None)
        full_name = data.get('name', '')
        first_name = data.get('given_name', '')
        last_name = data.get('family_name', '')

        user = sociallogin.user
        user.email = email
        user.full_name = full_name or f"{first_name} {last_name}"
        user.username = email.split("@")[0]  
        user.is_active = True 
        user.date_joined = now()

        
        if 'phone_number' in data:
            user.phone_number = data['phone_number']
        user.save()

        return user

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)
        # Ensure username is set (your User model still has a username field)
        if not user.username:
            user.username = user.email.split('@')[0]  # fallback
        # First name and last name come from Google
        if not user.first_name:
            user.first_name = data.get('first_name', '')
        if not user.last_name:
            user.last_name = data.get('last_name', '')
        return user
    


    
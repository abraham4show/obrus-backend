import logging
logger = logging.getLogger(__name__)
from users.models import User
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        try:
            user = super().populate_user(request, sociallogin, data)
            user.email = data.get('email')
            user.first_name = data.get('first_name', '')
            user.last_name = data.get('last_name', '')
            if not user.username:
                base_username = user.email.split('@')[0]
                username = base_username
                counter = 1
                while User.objects.filter(username=username).exists():
                    username = f"{base_username}{counter}"
                    counter += 1
                user.username = username
            return user
        except Exception as e:
            logger.error(f"Error in populate_user: {e}", exc_info=True)
            raise
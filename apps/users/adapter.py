import logging
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model
from allauth.socialaccount.models import SocialAccount

User = get_user_model()
logger = logging.getLogger(__name__)

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        logger.debug(f"Populating user with data: {data}")
        user = super().populate_user(request, sociallogin, data)

        user.email = data.get('email')
        user.first_name = data.get('first_name', '')
        user.last_name = data.get('last_name', '') or ''

        # Generate unique username
        base_username = user.email.split('@')[0]
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        user.username = username

        # Force save the user now (bypass allauth’s pipeline if needed)
        try:
            user.save()
            logger.info(f"User saved directly: {user.email}")
        except Exception as e:
            logger.error(f"Direct save failed: {e}", exc_info=True)
            raise

        # Also associate the social account if not already
        sociallogin.user = user
        # sociallogin.account.user = user  # will be set in save()
        return user

    def save_user(self, request, sociallogin, form=None):
        try:
            user = super().save_user(request, sociallogin, form)
            logger.info(f"User saved via allauth: {user.email}")
            return user
        except Exception as e:
            logger.error(f"Error in save_user: {e}", exc_info=True)
            raise
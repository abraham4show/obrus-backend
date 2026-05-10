import logging
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model

User = get_user_model()
logger = logging.getLogger(__name__)

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        logger.debug(f"Populating user with data: {data}")
        user = super().populate_user(request, sociallogin, data)

        # Explicitly set fields from Google
        user.email = data.get('email')
        user.first_name = data.get('first_name', '')
        user.last_name = data.get('last_name', '')

        # Generate a unique username (your User model requires it)
        base_username = user.email.split('@')[0]
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        user.username = username

        logger.info(f"User prepared: email={user.email}, username={user.username}, first_name={user.first_name}, last_name={user.last_name}")
        return user

    def save_user(self, request, sociallogin, form=None):
        """Override to log any error during saving"""
        try:
            user = super().save_user(request, sociallogin, form)
            logger.info(f"User saved successfully: {user.email}")
            return user
        except Exception as e:
            logger.error(f"Failed to save user: {e}", exc_info=True)
            raise


        
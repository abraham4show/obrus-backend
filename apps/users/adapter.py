import logging
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()
logger = logging.getLogger(__name__)

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        """
        Called before social login. If a user with the same email already exists,
        connect the social account to that user.
        """
        email = sociallogin.account.extra_data.get('email')
        if not email:
            return

        try:
            existing_user = User.objects.get(email=email)
            # Connect the social account to the existing user
            sociallogin.connect(request, existing_user)
            logger.info(f"Connected social account to existing user: {email}")
        except User.DoesNotExist:
            logger.debug(f"No existing user for email: {email}")
        except Exception as e:
            logger.error(f"Error in pre_social_login: {e}", exc_info=True)

    def populate_user(self, request, sociallogin, data):
        """
        Populate user fields from Google data, but do NOT save.
        """
        logger.debug(f"Populating user with data: {data}")
        user = super().populate_user(request, sociallogin, data)

        user.email = data.get('email')
        user.first_name = data.get('first_name', '')
        user.last_name = data.get('last_name', '') or ''

        # Generate a unique username (required by User model)
        base_username = user.email.split('@')[0]
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        user.username = username

        # Do NOT save here – let allauth handle saving after email uniqueness checks
        return user

    def save_user(self, request, sociallogin, form=None):
        """
        Save the user after all checks. Log success/failure.
        """
        try:
            user = super().save_user(request, sociallogin, form)
            logger.info(f"User saved successfully via allauth: {user.email}")
            return user
        except Exception as e:
            logger.error(f"Error saving user: {e}", exc_info=True)
            raise
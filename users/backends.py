"""
Custom authentication backend for phone number login.
"""
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class PhoneNumberBackend(ModelBackend):
    """
    Custom authentication backend that uses phone number instead of username.
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate user by phone number and password.
        The 'username' parameter is actually the phone number.
        """
        if username is None:
            username = kwargs.get('phone_number')
        
        if username is None or password is None:
            return None
        
        try:
            user = User.objects.get(phone_number=username)
        except User.DoesNotExist:
            # Run the default password hasher once to reduce timing
            # difference between existing and non-existing users.
            User().set_password(password)
            return None
        
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        
        return None
    
    def get_user(self, user_id):
        """
        Get user by ID.
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

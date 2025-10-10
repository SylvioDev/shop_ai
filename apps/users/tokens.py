# tokens.py
from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six

class OneTimeUseTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        # Include whether the token was used in the hash
        return f"{user.pk}{timestamp}{user.userprofile.reset_token_used}"

one_time_use_token_generator = OneTimeUseTokenGenerator()
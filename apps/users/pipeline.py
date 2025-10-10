# myapp/pipeline.py

from django.contrib.auth import get_user_model
from social_core.exceptions import AuthForbidden
from django.shortcuts import redirect
import logging


logger = logging.getLogger(__name__)

User = get_user_model()

def prevent_duplicate_email(strategy, details, backend, user=None, *args, **kwargs):
    email = details.get('email')
    logger.debug(f"[SOCIAL AUTH] Email from provider: {email}")

    if user is None and email:
        if User.objects.filter(email=email).exists():
            logger.debug(f"[SOCIAL AUTH] Email {email} already exists, blocking new signup.")
            return redirect('login-error')
    
from django.contrib.auth.models import User
from social_core.exceptions import AuthForbidden

# List of Google emails allowed to log in as admin.
# Replace these with your actual team's Google emails.
ALLOWED_ADMIN_EMAILS = [
    'lgguillen@up.edu.ph',
    'jgcasquejo@up.edu.ph',
    'kcdongon@up.edu.ph',
]

def restrict_to_known_admins(backend, details, user=None, *args, **kwargs):
    """
    Custom social-auth pipeline step.
    Raises AuthForbidden if the Google account email is not in ALLOWED_ADMIN_EMAILS.
    """
    email = details.get('email', '')
    if email not in ALLOWED_ADMIN_EMAILS:
        raise AuthForbidden(backend)

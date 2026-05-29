from django.contrib.auth.models import User
from social_core.exceptions import AuthForbidden

# List of Google emails allowed to log in as admin.
# Replace these with your actual team's Google emails.
ALLOWED_ADMIN_EMAILS = [
    "lgguillen@up.edu.ph",
    "jgcasquejo@up.edu.ph",
    "kcdongon@up.edu.ph",
    "jeycelanntabon@gmail.com",
    "vbcalag@up.edu.ph",
]


def restrict_to_known_admins(backend, details, request, user=None, *args, **kwargs):
    """
    Custom social-auth pipeline step.
    Raises AuthForbidden if the Google account email is not in ALLOWED_ADMIN_EMAILS.
    """
    email = details.get("email", "")
    if email not in ALLOWED_ADMIN_EMAILS:
        # Store the attempted email so the error page can show it
        request.session["failed_login_email"] = email
        raise AuthForbidden(backend)

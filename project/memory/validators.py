import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_location(location: str):
    """
    Validate location field
    Valid string must contain square brackets with to floats inside
    Floats must be separated by a comma without spaces
    """
    if re.match(r'^\[\d+\.\d+,\d+\.\d+\]$', location) is None:
        raise ValidationError(
            _('Invalid location field: %(location)s'),
            code="invalid",
            params={"location": location}
        )

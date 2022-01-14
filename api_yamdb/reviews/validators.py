import datetime

from django.core.validators import BaseValidator
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


@deconstructible
class MaxYearValidator(BaseValidator):
    message = _('Ensure this value is less than or equal to %(limit_value)s.')
    code = 'max_year_value'

    def __init__(self, message=None):
        self.limit_value = datetime.datetime.now().year
        if message:
            self.message = message

    def compare(self, a, b):
        return a > b

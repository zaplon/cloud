import re

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.deconstruct import deconstructible
from django.utils.translation import ugettext_lazy as _


EMPTY_VALUES = (None, '', [], (), {})


class NIPValidator(RegexValidator):

    error_messages = {
        'invalid': _('Enter a tax number field (NIP) in the format XXX-XXX-XX-XX, XXX-XX-XX-XXX or XXXXXXXXXX.'),
        'checksum': _('Wrong checksum for the Tax Number (NIP).'),
    }

    def __init__(self, *args, **kwargs):
        kwargs['regex'] = r'^\d{3}-\d{3}-\d{2}-\d{2}$|^\d{3}-\d{2}-\d{2}-\d{3}$|^\d{10}$'
        super(NIPValidator, self).__init__(*args, **kwargs)

    def __call__(self, value):
        super(NIPValidator, self).__call__(value)
        if value in EMPTY_VALUES:
            return ''
        value = re.sub("[-]", "", value)
        if not self.has_valid_checksum(value):
            raise ValidationError(self.error_messages['checksum'])
        return '%s' % value

    def has_valid_checksum(self, number):
        """
        Calculates a checksum with the provided algorithm.
        """
        multiple_table = (6, 5, 7, 2, 3, 4, 5, 6, 7)
        result = 0
        for i in range(len(number) - 1):
            result += int(number[i]) * multiple_table[i]

        result %= 11
        if result == int(number[-1]):
            return True
        else:
            return False


class REGONValidator(RegexValidator):

    def __init__(self, *args, **kwargs):
        kwargs['regex'] = r'^\d{9,14}$'
        super(REGONValidator, self).__init__(*args, **kwargs)

    error_messages = {
        'invalid': _('National Business Register Number (REGON) consists of 9 or 14 digits.'),
        'checksum': _('Wrong checksum for the National Business Register Number (REGON).'),
    }

    def __call__(self, value):
        super(REGONValidator, self).__call__(value)
        if value in EMPTY_VALUES:
            return ''
        if not self.has_valid_checksum(value):
            raise ValidationError(self.error_messages['checksum'])
        return '%s' % value

    def has_valid_checksum(self, number):
        """
        Calculates a checksum with the provided algorithm.
        """
        weights = (
            (8, 9, 2, 3, 4, 5, 6, 7, -1),
            (2, 4, 8, 5, 0, 9, 7, 3, 6, 1, 2, 4, 8, -1),
            (8, 9, 2, 3, 4, 5, 6, 7, -1, 0, 0, 0, 0, 0),
        )

        weights = [table for table in weights if len(table) == len(number)]

        for table in weights:
            checksum = sum([int(n) * w for n, w in zip(number, table)])

            mod_result = checksum % 11

            if mod_result == 10 and number[-1] != '0':
                return False

            if mod_result % 10:
                return False

        return bool(weights)

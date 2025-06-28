"""Exceptions"""


class SendMessageError(Exception):
    """Error when trying to send message"""


class InvalidTwoFactorCode(Exception):
    """Invalid Two-Factor Authentication (2FA) code"""


class NoKeysForDecryptThisMessage(Exception):
    """
    No keys to decrypt this message
    If you created a new key then you need to re-login
    If you deleted the key then you can't decrypt this message
    """


class LoadSessionError(Exception):
    """Error while loading session, maybe this session file was created in other version? Try re-login."""


class AddressNotFound(Exception):
    """Email address was not found"""

class CantSolveImageCaptcha(Exception):
    """Error when trying to solve image CAPTCHA, maybe this image hard, just retry login"""


class InvalidCaptcha(Exception):
    """CAPTCHA solved, but something got wrong"""

"""Dataclasses."""
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional, Callable


class LoginType(Enum):
    """
    Login type

    Attributes:
        WEB: Harder auth, more requests, CAPTCHA like in web
        DEV: Simpler auth, fewer requests, maybe more often CAPTCHA
    """
    WEB = 'web'
    DEV = 'dev'


def default_function_for_manual_solve_captcha(auth_data: dict) -> str:
    """ Default function to manual solve CAPTCHA. """
    print("Open the URL below on a web browser in incognito mode:")
    print(f"URL: {auth_data['Details']['WebUrl']}\n")
    print("Follow the instructions on https://github.com/opulentfox-29/protonmail-api-client/blob/master/README.md#captcha to get token.")
    token_from_init = input('Enter the token: ')
    return token_from_init

def get_token_from_url(url):
    import urllib.parse
    parsed_url = urllib.parse.urlparse(url)
    parsed_query = urllib.parse.parse_qs(parsed_url.query)
    return parsed_query.get('token', [''])[0]

def default_function_for_pyqt_solve_captcha(auth_data: dict) -> str:
    """ Default function to solve CAPTCHA using PyQt web browser. """

    import os
    import sys
    from PyQt6.QtWidgets import QApplication, QMainWindow
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    from PyQt6.QtWebEngineCore import QWebEngineUrlRequestInterceptor, QWebEngineProfile, QWebEnginePage
    from PyQt6.QtCore import QUrl, QLoggingCategory

    QLoggingCategory("qt.webenginecontext").setFilterRules("*.info=false")
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = f"--enable-logging --log-level=3"

    url = auth_data['Details']['WebUrl']

    class QuietWebEnginePage(QWebEnginePage):
        #js messages spam the console for no reason
        def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
            return

    class RequestInterceptor(QWebEngineUrlRequestInterceptor):
        def __init__(self):
            super().__init__()
            self.token = ''
        def interceptRequest(self, info):
            url_str = info.requestUrl().toString()
            if "verify-api.proton.me/captcha/v1/api/bg" in url_str:
                # This URL has the token we need
                self.token = get_token_from_url(url_str)
            if "verify-api.proton.me/captcha/v1/api/finalize" in url_str:
                # This URL is when the CAPTCHA is solved, we can quit the app
                QApplication.instance().quit()

    class BrowserWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("OAuth2 Login")
            self.resize(800, 600)
            self.browser = QWebEngineView()
            self.browser.setPage(QuietWebEnginePage(self.browser))
            self.setCentralWidget(self.browser)
            self.browser.load(QUrl(url))
            self.show()

    webapp = QApplication(sys.argv)
    interceptor = RequestInterceptor()
    QWebEngineProfile.defaultProfile().setUrlRequestInterceptor(interceptor)
    window = BrowserWindow()
    webapp.exec()

    return interceptor.token

@dataclass
class CaptchaConfig:
    """ Config to solve CAPTCHA. """
    class CaptchaType(Enum):
        """
        CAPTCHA solve type

        Attributes:
            AUTO: Attempt fully automatic CAPTCHA solution. It does not guarantee the result, sometimes it is necessary to run several times.
            MANUAL: Manual CAPTCHA solution. Requires additional actions from you, read more: https://github.com/opulentfox-29/protonmail-api-client?tab=readme-ov-file#solve-captcha
            PYQT: Use PyQt6 web browser to solve CAPTCHA.
        """
        AUTO = 'auto'
        MANUAL = 'manual'
        PYQT = 'pyqt'

    type: CaptchaType = CaptchaType.AUTO
    function_for_manual: Callable = default_function_for_manual_solve_captcha
    function_for_pyqt: Callable = default_function_for_pyqt_solve_captcha


@dataclass
class UserMail:
    """User."""
    name: str = ''
    address: str = ''
    extra: dict = field(default_factory=dict)

    def __str__(self):
        return f"<UserMail [{self.address}]>"

    def to_dict(self) -> dict[str, any]:
        """
        Object to dict

        :returns: :py:obj:`dict`
        """
        return asdict(self)

@dataclass
class AccountAddress:
    """One user can have many addresses."""
    id: str = ''
    email: str = ''
    name: str = ''

    def __str__(self):
        return f"<AccountAddress [{self.email}, {self.name}]>"

    def to_dict(self) -> dict[str, any]:
        """
        Object to dict

        :returns: :py:obj:`dict`
        """
        return asdict(self)

@dataclass
class Message:
    """Message."""
    id: str = ''
    conversation_id: str = ''
    subject: str = ''
    unread: bool = False
    sender: UserMail = field(default_factory=UserMail)
    recipients: list[UserMail] = field(default_factory=list)
    cc: list[UserMail] = field(default_factory=list)
    bcc: list[UserMail] = field(default_factory=list)
    time: int = 0
    size: int = 0
    body: str = ''
    type: str = ''
    external_id: str = ''
    in_reply_to: str = ''
    plain_transfer_encoding: str = field(default='quoted-printable')
    extra: dict = field(default_factory=dict)

    def __str__(self):
        ellipsis_str = '...' if len(self.subject) > 20 else ','
        cropped_subject = self.subject[:20]
        return f"<Message [{cropped_subject}{ellipsis_str} id: {self.id[:10]}...]>"

    def to_dict(self) -> dict[str, any]:
        """
        Object to dict

        :returns: :py:obj:`dict`
        """
        return asdict(self)

@dataclass
class PgpPairKeys:
    """PGP pair keys."""
    is_primary: bool = False
    is_user_key: bool = False
    fingerprint_public: Optional[str] = None
    fingerprint_private: Optional[str] = None
    public_key: Optional[str] = None
    private_key: Optional[str] = None
    passphrase: Optional[str] = None
    email: Optional[str] = None

    def __str__(self):
        fingerprint = self.fingerprint_private or self.fingerprint_public
        return f"<PGPKey [{fingerprint or None}, is_primary: {self.is_primary}, is_user_key: {self.is_user_key}]>"

    def to_dict(self) -> dict[str, any]:
        """
        Object to dict

        :returns: :py:obj:`dict`
        """
        return asdict(self)

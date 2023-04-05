from .api import bake_url
from time import time
from ast import literal_eval
from tempfile import gettempdir
from os.path import join as path_join

OAUTH_URL = "https://oauth.vk.com/authorize"

Token = str


class Storage:
    """Stores access tokens in temp dir."""

    _tokens_file: str = "vkstatus.tokens"
    _tokens: dict[str, tuple[Token, float]]

    def __init__(self) -> None:
        self._tokens_path = path_join(gettempdir(), self._tokens_file)
        try:
            with open(self._tokens_path) as file:
                # not safest
                self._tokens = literal_eval(file.read())
        except FileNotFoundError:
            self._tokens = {}

    def get_token(self, app_id: str) -> Token:
        """Get valid access token."""
        if (token := self._tokens.get(app_id, ("", 0)))[1] > time():
            return token[0]
        return ""

    def dump_tokens(self):
        """Save tokens to file."""
        with open(self._tokens_path, "w") as file:
            file.write(repr(self._tokens))

    def update_token(self, app_id: str, access_token: Token) -> None:
        """Replace token and set its expiration time(24h)."""
        self._tokens[app_id] = (access_token, time() + 86400)
        self.dump_tokens()


def generate_auth_link(app_id: str) -> str:
    """Generate link for authorization with access to status only."""
    args = {
        "client_id": app_id,
        "scope": 1024,  # status
        "redirect_uri": "https://oauth.vk.com/blank.html",
        "response_type": "token",
        "revoke": "1",
    }
    return bake_url(OAUTH_URL, args=args)


def parse_token(text: str) -> Token:
    """Get token from string."""
    text = "".join(text.split())
    try:
        token_start = text.index("access_token=") + 13
        return text[token_start : text.index("&", token_start)]
    except ValueError:
        return text

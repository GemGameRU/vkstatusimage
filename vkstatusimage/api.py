import urllib.request
from json import loads

Token: type = str

API_URL = r"https://api.vk.com/"
API_VERSION = "5.131"


class TokenError(Exception):
    """Raised when an error occurs while retrieving a token."""

    def __init__(self, data: dict) -> None:
        self.message = data["error_msg"]
        self.data = data
        super().__init__(self.message)


def bake_url(url: str, args: dict) -> str:
    """Bakes a URL with the given arguments."""
    if len(args.keys()):
        return rf"{url}?{'&'.join([rf'{key}={val}' for key, val in args.items()])}"
    else:
        return url


def _generate_method_url(method: str, args: dict | None = None) -> str:
    """Generate method url for api."""
    if args is None:
        return f"https://api.vk.com/method/{method}"
    return bake_url(f"https://api.vk.com/method/{method}", args)


def _vkapi_request(
    method: str,
    access_token: str,
    args: dict | None = None,
    ignore_error: bool = False,
) -> dict:
    """
    Make api call for specified method.
    client_id not needed because api can specify it from access_token.
    """
    if args is None:
        args = {}
    _args = {
        **args,
        "method": method,
        "v": API_VERSION,
        "access_token": access_token,
        "format": "json",
    }
    url = _generate_method_url(method, _args)
    with urllib.request.urlopen(url) as _page:
        response = loads(_page.read().decode("utf-8"))
    if not ignore_error and "error" in response.keys():
        raise TokenError(response["error"])
    else:
        return response["response"]


# Api method calls start here.


def set_status(access_token: Token, status_id: int | str) -> dict:
    """Set status id via api call."""
    return _vkapi_request("status.setImage", access_token, {"status_id": status_id})


def get_statuses_list(access_token: Token) -> list[dict]:
    """Retrieve all statuses via api call."""
    return sorted(
        _vkapi_request("status.getImageList", access_token)["items"],
        key=lambda x: x["id"],
    )


def get_status(access_token: Token) -> dict:
    """Retrieve status id and name via api call."""
    return _vkapi_request("status.getImage", access_token)["status"]

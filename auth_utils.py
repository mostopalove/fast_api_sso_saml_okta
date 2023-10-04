# The goal of this file is to check whether the request is authorized or not [verification of the protected route]
from typing import Optional
from fastapi import Request, HTTPException
from fastapi.security import APIKeyCookie

from saml_constants import USER_DATA_KEY, SESSION_COOKIE_KEY


async def prepare_from_fastapi_request(request: Request):
    form_data = await request.form()

    rv = {
        "http_host": request.url.hostname,
        "server_port": request.url.port,
        "script_name": request.url.path,
        "post_data": {},
        "get_data": request.query_params if request.query_params else {}
        # Advanced request options
        # "https": "",
        # "request_uri": "",
        # "query_string": "",
        # "validate_signature_from_qs": False,
        # "lowercase_urlencoding": False
    }
    if "SAMLResponse" in form_data:
        saml_response = form_data["SAMLResponse"]
        rv["post_data"]["SAMLResponse"] = saml_response
    if "RelayState" in form_data:
        relay_state = form_data["RelayState"]
        rv["post_data"]["RelayState"] = relay_state
    return rv


class SessionChecker(APIKeyCookie):
    def __init__(self, name: str = SESSION_COOKIE_KEY):
        super(SessionChecker, self).__init__(name=name)

    async def __call__(self, request: Request):
        session = request.session
        saml_data = session.get(USER_DATA_KEY)
        api_key: Optional[str] = await super(SessionChecker, self).__call__(request)

        if saml_data:
            return api_key
        else:
            raise HTTPException(status_code=401, detail="Unauthorized")

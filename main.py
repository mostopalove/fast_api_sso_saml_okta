from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from onelogin.saml2.auth import OneLogin_Saml2_Auth, OneLogin_Saml2_Error

from auth_utils import SessionChecker, prepare_from_fastapi_request
from saml_constants import OKTA_SSO_URL, SAML_SETTINGS, USER_DATA_KEY, SESSION_SECRET_KEY, SESSION_COOKIE_KEY

app = FastAPI()


twelve_hours_in_seconds = 12 * 60 * 60
app.add_middleware(SessionMiddleware,
                   secret_key=SESSION_SECRET_KEY,
                   session_cookie=SESSION_COOKIE_KEY,
                   max_age=twelve_hours_in_seconds)


@app.get("/sso/login")
async def sso_login():
    return RedirectResponse(OKTA_SSO_URL)


@app.post("/sso/acs")
async def sso_acs(request: Request):
    try:
        req = await prepare_from_fastapi_request(request)
        auth = OneLogin_Saml2_Auth(req, SAML_SETTINGS)
        auth.process_response()
        errors = auth.get_errors()
        if not errors:
            if auth.is_authenticated():
                request.session[USER_DATA_KEY] = auth.get_attributes()
            else:
                raise HTTPException(status_code=403, detail="Not authenticated")
        else:
            raise HTTPException(status_code=403, detail=f"Error when processing SAML response: {', '.join(errors)}")
    except OneLogin_Saml2_Error as e:
        raise HTTPException(status_code=403, detail=f"An error occurred: {e}")

    return {"message": "Authenticated"}
    # return RedirectResponse('/protected-resource', status_code=status.HTTP_302_FOUND)


@app.get("/protected-resource", dependencies=[Depends(SessionChecker())])
async def protected_resource():
    return {"message": "I am protected!"}


@app.get("/")
async def root():
    return {"message": "Hello World"}

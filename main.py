from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from saml2 import BINDING_HTTP_POST, BINDING_HTTP_REDIRECT
from saml2.client import Saml2Client
from saml2.config import Config as Saml2Config

app = FastAPI()


# SAML configuration
# Audience Restriction
OKTA_ENTITY_ID = 'http://localhost:8000'
# Identity Provider Single Sign-On URL
OKTA_SSO_URL = 'https://dev-62477416.okta.com/app/dev-62477416_samltestapp_1/exkatg6gjmlgcxm6O5d7/sso/saml'
# Sign out URL
OKTA_SIGN_OUT_URL = 'https://dev-62477416.okta.com'
# Identity Provider Issuer
OKTA_ISSUER = 'http://www.okta.com/exkatg6gjmlgcxm6O5d7'
# X.509 Certificate:
OKTA_CERTIFICATE = '''
-----BEGIN CERTIFICATE-----
MIIDqDCCApCgAwIBAgIGAYn40DhtMA0GCSqGSIb3DQEBCwUAMIGUMQswCQYDVQQGEwJVUzETMBEG
A1UECAwKQ2FsaWZvcm5pYTEWMBQGA1UEBwwNU2FuIEZyYW5jaXNjbzENMAsGA1UECgwET2t0YTEU
MBIGA1UECwwLU1NPUHJvdmlkZXIxFTATBgNVBAMMDGRldi02MjQ3NzQxNjEcMBoGCSqGSIb3DQEJ
ARYNaW5mb0Bva3RhLmNvbTAeFw0yMzA4MTUxMDQ4MDJaFw0zMzA4MTUxMDQ5MDJaMIGUMQswCQYD
VQQGEwJVUzETMBEGA1UECAwKQ2FsaWZvcm5pYTEWMBQGA1UEBwwNU2FuIEZyYW5jaXNjbzENMAsG
A1UECgwET2t0YTEUMBIGA1UECwwLU1NPUHJvdmlkZXIxFTATBgNVBAMMDGRldi02MjQ3NzQxNjEc
MBoGCSqGSIb3DQEJARYNaW5mb0Bva3RhLmNvbTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoC
ggEBAMKWjEiY7s9dhgsQ4lv1E/oDBqUMOauCynvwfFu9q6e6NABvLyPKthX3L4txPnQQwOczCysS
6pZ+r2XD/3gBI8m8MqOLaV/Z8ACD0Hv616a0k0+ed2lcHyBdU/w7tb70pkUk5YPwySHgjWhPFduY
Q8XzkLq9Kxe6wBADBAKIby9TdEsV4E04xJDR1VNJIcOqVasbQQS0tVVYg0ww6IRNvvC+DHLuAH5t
HWdFNnlmID2iOn0/ONMAaVoC7A3CXoZ87rK0ta6wCggIRZpoA+vXknOgrN6OQ2hXtmJLYG3S2Hvi
j33nHm/DajzSkb0+Z6BpXGhiVXL5AaRgFZX/4Z+OBLcCAwEAATANBgkqhkiG9w0BAQsFAAOCAQEA
F/TkcN2erDPofDdLC2WWf4uQHPdQXgVRDKojFo0cMOU1TDu001c9Nqw7BJHTQI8HPKnBn9hI/6hb
iN3Kw4hUM45lA9WvHAEyP/6pFFkT7lqYhPfVLv+XreV63UISDnuix9AeoHgcyhYCf4rg1XMsk7Jf
Vv6yi7bJVcRwNSSLIYX+vdH/nRuM321D7Cn9v/9Umb4w/p62ikEr1GMfhTzKq9OpHVP+wi8aKD65
G5Wz9WyOgJgvGZCrdeMIL3lDCQlhB28Knb7rVazPtVMYLKMxHzc98Vp+9XTTjfpyjsCcAL6o4i0l
ZIJGMhI/859jOrOlbrpzS753xUxfF6sdvZYLWg==
-----END CERTIFICATE------
'''

CONFIG = {
    "debug": True,
    "entityid": OKTA_ENTITY_ID,
    "name": "SAML Test App",
    "service": {
        "idp": {
            "endpoints": {
                "single_sign_on_service": [
                    (
                        OKTA_SSO_URL,
                        BINDING_HTTP_REDIRECT,
                    ),
                ],
                "single_logout_service": [
                    (
                        OKTA_SIGN_OUT_URL,
                        BINDING_HTTP_REDIRECT,
                    ),
                ],
            },
            "x509cert": OKTA_CERTIFICATE,
        }
    }
}


@app.middleware("http")
async def validate_user(request: Request, call_next):
    # end_point = request.url.path
    # request.session["name"] = "some random value"
    print(request.session)
    response = await call_next(request)
    return response

app.add_middleware(SessionMiddleware, secret_key='my-secret-key')


@app.get("/sso/login")
async def sso_login():
    return RedirectResponse(OKTA_SSO_URL)


@app.post("/sso/acs")
async def sso_acs(request: Request):
    config = Saml2Config()
    config.load(CONFIG)
    client = Saml2Client(config=config)
    authn_response = await request.form()
    client.parse_authn_request_response(authn_response.get('SAMLResponse'), BINDING_HTTP_POST)
    return {"message": "Successfully logged in"}


@app.get("/protected-resource")
async def protected_resource():
    pass


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

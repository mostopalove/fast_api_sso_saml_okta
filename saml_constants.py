import os
from pathlib import Path
from dotenv import load_dotenv

APP_PATH = os.path.dirname(os.path.realpath(__file__))
RELATIVE_ֹPATH = str(Path(str(os.path.dirname(os.path.realpath(__file__)))))
DOTENV_PATH = '/.env'
# load .env file for local run
load_dotenv(RELATIVE_ֹPATH + DOTENV_PATH)


# SAML configuration
# Audience Restriction
OKTA_ENTITY_ID = os.environ.get('OKTA_ENTITY_ID')
# Identity Provider Single Sign-On URL
OKTA_SSO_URL = os.environ.get('OKTA_SSO_URL')
# Identity Provider Issuer
OKTA_ISSUER = os.environ.get('OKTA_ISSUER')
# X.509 Certificate:
OKTA_CERTIFICATE = os.environ.get('OKTA_CERTIFICATE')

SAML_SETTINGS = {
    "debug": True,
    "idp": {
        "entityId": OKTA_ISSUER,
        "singleSignOnService": {
            "url": OKTA_SSO_URL,
            "binging": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
        },
        "x509cert": OKTA_CERTIFICATE
    },
    "sp": {
        "entityId": OKTA_ENTITY_ID,
        "assertionConsumerService": {
            "url": f"{OKTA_ENTITY_ID}/sso/acs",
            "binging": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
        }
    }
}

SESSION_SECRET_KEY = 'super-secret-key'
SESSION_COOKIE_KEY = 'session'

USER_DATA_KEY = 'SAMLUserData'

"""
This module contains utilities for working with JSON Web Tokens & OAuth 2.0

Sources:
- RFC 6749 OAuth 2.0 Authorization Framework
- RFC 8693 OAuth 2.0 Token Exchange
"""

from enum import StrEnum
from typing import TypedDict, TypeGuard


class OAuth2Field(StrEnum):
    Act = "act"
    """indicates the current party acting on behalf of the original party"""
    Scope = "scope"
    """indicates the permissions granted to the application"""
    MayAct = "may_act"
    """defines whether the bearer may act on behalf of another"""
    ClientId = "client_id"
    """client identifier making the requests"""


class JwtClaim(StrEnum):
    Issuer = "iss"
    Subject = "sub"
    Audience = "aud"
    ExpirationTime = "exp"
    NotBefore = "nbf"
    IssuedAt = "iat"
    JwtId = "jti"
    Act = OAuth2Field.Act.value
    Scope = OAuth2Field.Scope.value
    MayAct = OAuth2Field.MayAct.value
    ClientId = OAuth2Field.ClientId.value


class JwtClaimDict(TypedDict, total=False):
    iss: str
    """issuer"""
    sub: str
    """subject"""
    aud: str
    """audience"""
    exp: str
    """expiration time"""
    nbf: str
    """not before"""
    iat: str
    """issued at"""
    jti: str
    """jwt id"""
    act: str
    """act; indicates the current party acting on behalf of the original party"""
    scope: str
    """scope; indicates the permissions granted to the application"""
    may_act: str
    """may act; defines whether the bearer may act on behalf of another"""
    client_id: str
    """client id; client identifier making the requests"""


def is_registered_claim(claim: str) -> TypeGuard[JwtClaim]:
    try:
        JwtClaim(claim)
        return True
    except:
        return False

from enum import StrEnum


ClaimSet = StrEnum


class ClaimOAuth2(ClaimSet):
    Act = "act"
    Scope = "scope"
    ClientId = "client_id"
    MayAct = "may_act"


class ClaimJwt(ClaimSet):
    Issuer = "iss"
    Subject = "sub"
    Audience = "aud"
    ExpirationTime = "exp"
    NotBefore = "nbf"
    IssuedAt = "iat"
    JwtId = "jti"

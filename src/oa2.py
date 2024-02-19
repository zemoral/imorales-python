from enum import StrEnum


class OAuth2Field(StrEnum):
    Act = "act"
    """Act; indicates the current party acting on behalf of the original party"""
    Scope = "scope"
    """Scope; indicates the permissions granted to the application"""
    MayAct = "may_act"
    """May act; defines whether the bearer may act on behalf of another"""
    ClientId = "client_id"
    """Client id; client identifier making the requests"""

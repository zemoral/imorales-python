"""
This module contains common utilities for working with OAuth 2.0

Sources:
- RFC 6749 OAuth 2.0 Authorization Framework
- RFC 8693 OAuth 2.0 Token Exchange
"""

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

"""Authentication example.

This module provides a demonstration of the AuthProvider class in LogicLayer.
It should not be considered safe for production, as it exists only to provide
an example and to enable the debug endpoints in tesseract.

In the real world, the user should implement at least the AuthProvider.get_roles
method with the matching set of roles from the user datastore.

The user is responsible to determine which token types are allowed and how to
interpret them, how to match that information with the User datastore, and to
return the set of roles according to the case.
"""

import dataclasses
from typing import Optional

from logiclayer import AuthProvider, AuthToken, AuthTokenType


@dataclasses.dataclass
class User:
    """Sample user dataclass."""

    id: str
    name: str
    roles: set[str]


# The 'sysadmin' role enables the responses in the debug endpoints
USERS = [
    User("d912ad5c", name="Alice", roles={"sysadmin", "pro"}),
    User("72f1d152", name="Bob", roles={"contributor"}),
]


class BaseAuthProvider(AuthProvider):
    """Defines a generic auth provider to enable debugging endpoints."""

    def _find_user_data(self, token: Optional["AuthToken"]) -> User | None:
        if not token:
            return None

        user_id = token.value if token.kind == AuthTokenType.SEARCHPARAM else ""

        return next((user for user in USERS if user.id == user_id), None)

    def get_roles(self, token: Optional["AuthToken"]) -> set[str]:
        """Resolve the set of roles associated with the token provided by a request."""
        user = self._find_user_data(token)
        return user.roles if user else {"visitor"}

    def get_user(self, token: Optional["AuthToken"]) -> dict[str, str] | None:
        """Resolve user information associated with the token provided by a request."""
        user = self._find_user_data(token)
        return dataclasses.asdict(user) if user else None

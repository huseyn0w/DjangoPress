"""API data-access for auth tokens (the single home for Token ORM)."""

from __future__ import annotations

from rest_framework.authtoken.models import Token


class TokenRepository:
    @staticmethod
    def get_or_create_for(user) -> str:
        token, _ = Token.objects.get_or_create(user=user)
        return token.key

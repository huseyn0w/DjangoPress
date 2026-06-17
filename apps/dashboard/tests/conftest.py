import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()


@pytest.fixture
def make_user(db):
    def _make(username: str, role: str | None = None, **extra):
        user = User.objects.create_user(username=username, password="pw", **extra)
        if role:
            user.groups.add(Group.objects.get(name=role))
        return user

    return _make

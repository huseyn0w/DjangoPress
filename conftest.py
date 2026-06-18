import pytest
from django.core.cache import cache
from django.utils import translation


@pytest.fixture(autouse=True)
def _clear_cache():
    """Clear the (process-global) cache around every test.

    SiteSettings and the active theme are cached; without this, a value set in
    one test could leak into another and make the suite order-dependent.
    """
    cache.clear()
    yield
    cache.clear()


@pytest.fixture(autouse=True)
def _reset_active_language():
    """Reset the thread-local active language around every test.

    LocaleMiddleware activates a request's language (e.g. a GET to /de/...) and
    does not reset it afterwards, so without this the activated language would
    leak into later tests and make URL reversing order-dependent.
    """
    translation.activate("en")
    yield
    translation.deactivate_all()

import pytest

from apps.plugins import hooks


@pytest.fixture(autouse=True)
def isolate_hook_registry():
    """Snapshot and restore the global hook registry around each test.

    Lets tests register throwaway hooks without leaking into other tests, while
    preserving the hooks that plugin AppConfigs registered at startup.
    """
    stores = (hooks._actions, hooks._filters, hooks._renders)
    snapshot = [{name: list(items) for name, items in store.items()} for store in stores]
    yield
    for store, saved in zip(stores, snapshot, strict=True):
        store.clear()
        store.update({name: list(items) for name, items in saved.items()})

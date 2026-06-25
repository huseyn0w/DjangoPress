"""Public menu services — resolve a managed menu into render-ready link dicts.

The view/template tag stays at the boundary; all data access goes through
``MenuRepository``. Returns plain dicts so templates never touch the ORM.
"""

from __future__ import annotations

from .repositories import MenuRepository


def get_menu_items(slug: str) -> list[dict[str, str]]:
    """Resolved ``[{label, url}]`` for the menu ``slug`` in order, or ``[]``.

    Labels and URLs are resolved per item (content links localise via the linked
    object's translated title); an empty list lets callers fall back to defaults.
    """
    menu = MenuRepository.get_by_slug(slug)
    if menu is None:
        return []
    return [
        {"label": item.get_label(), "url": item.get_url()}
        for item in MenuRepository.items_for(menu)
    ]

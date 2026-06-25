"""Menus data-access layer. The single home for menu ORM access."""

from __future__ import annotations

from django.db.models import QuerySet
from django.shortcuts import get_object_or_404

from .models import Menu, MenuItem


class MenuRepository:
    @staticmethod
    def all() -> QuerySet:
        return Menu.objects.all()

    @staticmethod
    def get(pk: int) -> Menu:
        return get_object_or_404(Menu, pk=pk)

    @staticmethod
    def get_by_slug(slug: str) -> Menu | None:
        return Menu.objects.filter(slug=slug).first()

    @staticmethod
    def items_for(menu: Menu) -> QuerySet:
        """A menu's items in order, with link targets joined to avoid N+1."""
        return menu.items.select_related("post", "page", "category")

    @staticmethod
    def delete(menu: Menu) -> None:
        menu.delete()


class MenuItemRepository:
    @staticmethod
    def get(menu: Menu, pk: int) -> MenuItem:
        return get_object_or_404(menu.items, pk=pk)

    @staticmethod
    def ordered(menu: Menu) -> list[MenuItem]:
        return list(menu.items.all())

    @staticmethod
    def next_position(menu: Menu) -> int:
        last = menu.items.order_by("-position").first()
        return (last.position + 1) if last else 0

    @staticmethod
    def delete(item: MenuItem) -> None:
        item.delete()

    @staticmethod
    def swap_positions(a: MenuItem, b: MenuItem) -> None:
        a.position, b.position = b.position, a.position
        a.save(update_fields=["position"])
        b.save(update_fields=["position"])

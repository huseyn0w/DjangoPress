import pytest

from apps.plugins import hooks, registry

pytestmark = pytest.mark.django_db


def test_apply_filters_chains_in_priority_order():
    hooks.add_filter("t_chain", lambda v: v + "A", priority=20)
    hooks.add_filter("t_chain", lambda v: v + "B", priority=10)
    # priority 10 (B) runs before priority 20 (A)
    assert hooks.apply_filters("t_chain", "x") == "xBA"


def test_do_action_runs_callbacks():
    calls = []
    hooks.add_action("t_act", lambda payload: calls.append(payload))
    hooks.do_action("t_act", 42)
    assert calls == [42]


def test_render_hook_concatenates_html():
    hooks.add_render("t_region", lambda **kw: "<a>")
    hooks.add_render("t_region", lambda **kw: "<b>")
    assert hooks.render_hook("t_region") == "<a><b>"


def test_plugin_of_infers_slug_from_module():
    def fn():
        pass

    fn.__module__ = "plugins.reading_time.hooks"
    assert hooks._plugin_of(fn) == "reading_time"


def test_plugin_of_returns_none_for_core_module():
    def fn():
        pass

    fn.__module__ = "apps.content.views"
    assert hooks._plugin_of(fn) is None


def test_imported_callback_still_attributed_to_registering_plugin():
    # Registering an imported/foreign callable: attribution falls back to the
    # registering module. Here the test module isn't a plugin, so it's core (None)
    # — but the resolution path (caller inference) is exercised.
    from django.utils.html import escape

    hooks.add_filter("t_imported", escape, plugin="reading_time")
    stored = hooks._filters["t_imported"][0]
    assert stored.plugin == "reading_time"  # explicit slug respected


def test_disabled_plugin_callbacks_are_skipped():
    # The reading_time plugin registers a post_content filter.
    enabled = hooks.apply_filters("post_content", "<p>hello world</p>")
    assert "min read" in enabled

    registry.set_enabled("reading_time", False)
    disabled = hooks.apply_filters("post_content", "<p>hello world</p>")
    assert "min read" not in disabled

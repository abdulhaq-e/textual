import pytest

from textual.widget import Widget
from textual.css.query import WrongType, NoMatches


def test_query():
    class View(Widget):
        pass

    class App(Widget):
        pass

    app = App()
    main_view = View(id="main")
    help_view = View(id="help")
    app._add_child(main_view)
    app._add_child(help_view)

    widget1 = Widget(id="widget1")
    widget2 = Widget(id="widget2")
    sidebar = Widget(id="sidebar")
    sidebar.add_class("float")

    helpbar = Widget(id="helpbar")
    helpbar.add_class("float")

    main_view._add_child(widget1)
    main_view._add_child(widget2)
    main_view._add_child(sidebar)

    sub_view = View(id="sub")
    sub_view.add_class("-subview")
    main_view._add_child(sub_view)

    tooltip = Widget(id="tooltip")
    tooltip.add_class("float", "transient")
    sub_view._add_child(tooltip)

    help = Widget(id="markdown")
    help_view._add_child(help)
    help_view._add_child(helpbar)

    # repeat tests to account for caching
    for repeat in range(3):
        assert list(app.query("Frob")) == []
        assert list(app.query(".frob")) == []
        assert list(app.query("#frob")) == []

        assert app.query("App")
        assert not app.query("NotAnApp")

        assert list(app.query("App")) == [app]
        assert list(app.query("#main")) == [main_view]
        assert list(app.query("View#main")) == [main_view]
        assert list(app.query("#widget1")) == [widget1]
        assert list(app.query("#widget2")) == [widget2]

        assert list(app.query("Widget.float")) == [sidebar, tooltip, helpbar]
        assert list(app.query(Widget).filter(".float")) == [sidebar, tooltip, helpbar]
        assert list(
            app.query(Widget)
            .exclude("App")
            .exclude("#sub")
            .exclude("#markdown")
            .exclude("#main")
            .exclude("#help")
            .exclude("#widget1")
            .exclude("#widget2")
        ) == [sidebar, tooltip, helpbar]
        assert list(reversed(app.query("Widget.float"))) == [helpbar, tooltip, sidebar]
        assert list(app.query("Widget.float").results(Widget)) == [
            sidebar,
            tooltip,
            helpbar,
        ]
        assert list(app.query("Widget.float").results(View)) == []

        assert app.query("Widget.float")[0] == sidebar
        assert app.query("Widget.float")[0:2] == [sidebar, tooltip]

        assert list(app.query("Widget.float.transient")) == [tooltip]

        assert list(app.query("App > View")) == [main_view, help_view]
        assert list(app.query("App > View#help")) == [help_view]
        assert list(app.query("App > View#main .float ")) == [sidebar, tooltip]
        assert list(app.query("View > View")) == [sub_view]

        assert list(app.query("#help *")) == [help, helpbar]
        assert list(app.query("#main *")) == [
            widget1,
            widget2,
            sidebar,
            sub_view,
            tooltip,
        ]

        assert list(app.query("App,View")) == [app, main_view, sub_view, help_view]
        assert list(app.query("#widget1, #widget2")) == [widget1, widget2]
        assert list(app.query("#widget1 , #widget2")) == [widget1, widget2]
        assert list(app.query("#widget1, #widget2, App")) == [app, widget1, widget2]

        assert app.query(".float").first() == sidebar
        assert app.query(".float").last() == helpbar

        with pytest.raises(NoMatches):
            _ = app.query(".no_such_class").first()
        with pytest.raises(NoMatches):
            _ = app.query(".no_such_class").last()

        with pytest.raises(WrongType):
            _ = app.query(".float").first(View)
        with pytest.raises(WrongType):
            _ = app.query(".float").last(View)

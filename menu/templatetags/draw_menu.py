from typing import Optional

from django import template
from django.utils.safestring import mark_safe

from ..models import Menu, MenuTree

register = template.Library()


def _gen_href(base: str, parents: list[int], menu_id: int) -> str:
    return (
        f"{base}?p="
        f"{','.join(map(str, parents)) + ',' if parents else ''}"
        f"{str(menu_id)}"
    )


def create_html(
    menu: MenuTree,
    depth: int,
    prefix: str = "",
    base="",
    selected_path=None,
    curr_depth: int = 1,
) -> str:
    """
    recursively creates html
    if menu has no children or curr_depth more than depth, then it returns prefix
    else it calls itself to generate children html
    """
    if curr_depth > depth:
        return prefix
    parents = menu.parents
    if selected_path is not None and selected_path[: len(parents)] != parents:
        return prefix

    is_same_path = [*parents, menu.id] == selected_path
    prefix = f"""{prefix}
        <li>
            {"<b>" if is_same_path else ""}
            <a href="{_gen_href(base=base, parents=parents, menu_id=menu.id)}">
                {menu.name}
            </a>
            {"</b>" if is_same_path else ""}
        </li>"""

    if not menu.children:
        return prefix

    for child_id, child in menu.children.items():
        prefix = (
            create_html(
                menu=child,
                prefix=prefix + "<ul>",
                base=base,
                curr_depth=curr_depth + 1,
                depth=depth,
                selected_path=selected_path,
            )
            + "</ul>"
        )

    return prefix


@register.simple_tag
def draw_menu(name="", selected_path=""):
    menu_trees = Menu.get_menu_tree(name)
    raw_html = ""
    selected_path = list(map(int, selected_path.split(","))) if selected_path else None
    for menu_id, menu in menu_trees.items():
        raw_html += "<ul>"
        if menu.children is not None:
            raw_html += create_html(
                menu,
                base="/" + menu.name,
                depth=len(selected_path) + 1 if selected_path else 2,
                selected_path=selected_path,
            )
        raw_html += "</ul>"
    return mark_safe(raw_html)

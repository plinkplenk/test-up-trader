from dataclasses import dataclass
from typing import Optional

from django.db import models, connection
from django.core.exceptions import ValidationError

from .apps import MenuConfig


@dataclass
class MenuTree:
    id: int
    name: str
    parent_id: Optional[int]
    children: dict[int, "MenuTree"]
    parents: list[int]
    depth: int

    def add_children(self, child: "MenuTree"):
        if not child.parents:
            # TODO: raise Exception
            return
        last_parent = self
        for parent_id in child.parents[1:]:
            last_parent = last_parent.children[parent_id]
        last_parent.children[child.id] = child


class Menu(models.Model):
    name = models.CharField(max_length=256)
    parent = models.ForeignKey(
        to="Menu", on_delete=models.CASCADE, null=True, blank=True
    )

    def clean(self):
        super().clean()
        if self.parent:
            parent = self.parent
            while parent is not None:
                if parent == self:
                    raise ValidationError("Child cannot be parent")
                parent = parent.parent

    @classmethod
    def get_menus(cls, name: str = ""):
        table_name = f"{MenuConfig.name}_{cls.__name__}"
        query = f"""        
            WITH RECURSIVE tree AS (
                SELECT id, name, parent_id, 0 AS depth, '' AS parents
                FROM menu_menu
                WHERE parent_id IS NULL {"AND name = %s" if name else ""}
                UNION ALL
                SELECT 
                    child_menu.id,
                    child_menu.name,
                    child_menu.parent_id, 
                    tree.depth + 1,
                    CASE
                        WHEN tree.parents = '' THEN tree.id
                        ELSE tree.parents || ',' || tree.id
                    END
                FROM tree
                    JOIN {table_name} child_menu ON child_menu.parent_id = tree.id
                )
            SELECT id, name, parent_id, depth, parents
            FROM tree
            ORDER BY depth, name;
            """
        with connection.cursor() as cursor:
            cursor.execute(query, ([name] if name else None))
            return cursor.fetchall()

    @classmethod
    def get_menu_tree(cls, name: str = "") -> dict[int, MenuTree]:
        menus = cls.get_menus(name)
        menu_trees: dict[int, MenuTree] = {}
        for menu_row in menus:
            menu_tree = MenuTree(
                id=menu_row[0],
                name=menu_row[1],
                parent_id=menu_row[2],
                depth=menu_row[3],
                parents=(
                    list(
                        map(
                            int,
                            parents.split(",") if (parents := str(menu_row[4])) else [],
                        )
                    )
                ),
                children={},
            )
            if menu_tree.parent_id is None:
                menu_trees[menu_tree.id] = menu_tree
            else:
                menu_trees[menu_tree.parents[0]].add_children(menu_tree)
        return menu_trees

    def __str__(self):
        return f"{self.id} - {self.name}"

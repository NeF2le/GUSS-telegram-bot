"""insert initialize data 2

Revision ID: 261411b2aca6
Revises: 912e1e85a85a
Create Date: 2024-07-19 12:55:51.586630

"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import Table, Column, MetaData, Integer, String


# revision identifiers, used by Alembic.
revision: str = "261411b2aca6"
down_revision: Union[str, None] = "912e1e85a85a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    activities_table = Table(
        "activities",
        MetaData(),
        Column("id", Integer, primary_key=True),
        Column("name", String)
    )
    categories_table = Table(
        "categories",
        MetaData(),
        Column("id", Integer, primary_key=True),
        Column("name", String)
    )
    op.bulk_insert(
        activities_table,
        [
            {"id": 1, "name": "vk_like"},
            {"id": 2, "name": "vk_comment"},
        ]
    )
    op.bulk_insert(
        categories_table,
        [
            {"id": 1, "name": "посещаемость"},
            {"id": 2, "name": "ответственность"},
            {"id": 3, "name": "продвижение гусс"}
        ]
    )


def downgrade() -> None:
    op.execute("DELETE FROM activities WHERE id IN (1, 2)")
    op.execute("DELETE FROM categories WHERE id IN (1, 2, 3)")

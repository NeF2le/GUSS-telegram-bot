"""insert initialize data

Revision ID: 912e1e85a85a
Revises: b6b8d5fea858
Create Date: 2024-07-19 12:54:40.327379

"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import Table, Column, MetaData, Integer, String


# revision identifiers, used by Alembic.
revision: str = "912e1e85a85a"
down_revision: Union[str, None] = "b6b8d5fea858"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    committees_table = Table(
        "committees",
        MetaData(),
        Column("id", Integer, primary_key=True),
        Column("name", String)
    )
    op.bulk_insert(
        committees_table,
        [
            {"id": 1, "name": "ЦВК"},
            {"id": 2, "name": "КДК"},
            {"id": 3, "name": "КОТ"},
            {"id": 4, "name": "СПОК"},
            {"id": 5, "name": "КЛЮКВА"},
            {"id": 6, "name": "ИЦ"},
        ]
    )


def downgrade() -> None:
    op.execute("DELETE FROM committees WHERE id IN (1, 2, 3, 4, 5, 6)")

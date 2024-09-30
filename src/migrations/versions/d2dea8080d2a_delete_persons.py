"""delete persons

Revision ID: d2dea8080d2a
Revises: 261411b2aca6
Create Date: 2024-07-21 10:32:41.691084

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d2dea8080d2a"
down_revision: Union[str, None] = "261411b2aca6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("DELETE FROM persons")


def downgrade() -> None:
    pass

"""Add 'protocols_document_id' column in 'committees' table

Revision ID: aea0f4e22fd3
Revises: d710e999260e
Create Date: 2024-08-02 13:06:51.186880

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "aea0f4e22fd3"
down_revision: Union[str, None] = "d710e999260e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "committees",
        sa.Column("protocols_document_id", sa.String(), nullable=True),
    )
    op.execute("UPDATE committees SET protocols_document_id = '1tbVlkHCNH4gHzUSLgGMYM99CxngJlW-_M61CdJWY6Yw' WHERE name = 'КЛЮКВА'")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("committees", "protocols_document_id")
    # ### end Alembic commands ###

"""Update ActionType enum

Revision ID: b6af27924b08
Revises: 7e6c70a9371e
Create Date: 2024-08-13 11:15:32.024861

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b6af27924b08"
down_revision: Union[str, None] = "7e6c70a9371e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "committees", "talisman", existing_type=sa.TEXT(), nullable=False
    )
    op.alter_column(
        "committees",
        "protocols_document_id",
        existing_type=sa.VARCHAR(),
        nullable=False,
    )
    op.execute("ALTER TYPE actiontype ADD VALUE 'UPDATE_PERSON_FIRST_NAME'")
    op.execute("ALTER TYPE actiontype ADD VALUE 'UPDATE_PERSON_LAST_NAME'")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "committees",
        "protocols_document_id",
        existing_type=sa.VARCHAR(),
        nullable=True,
    )
    op.alter_column(
        "committees", "talisman", existing_type=sa.TEXT(), nullable=True
    )
    op.execute("ALTER TYPE actiontype DROP VALUE 'UPDATE_PERSON_FIRST_NAME'")
    op.execute("ALTER TYPE actiontype DROP VALUE 'UPDATE_PERSON_LAST_NAME'")
    # ### end Alembic commands ###

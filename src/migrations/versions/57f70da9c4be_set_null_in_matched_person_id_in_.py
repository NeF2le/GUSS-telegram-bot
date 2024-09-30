"""Set null in 'matched_person_id' in EventTablePerson model

Revision ID: 57f70da9c4be
Revises: 82cf54ca59e5
Create Date: 2024-09-18 17:10:19.099189

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "57f70da9c4be"
down_revision: Union[str, None] = "82cf54ca59e5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(
        "event_registration_table_persons_matched_person_id_fkey",
        "event_registration_table_persons",
        type_="foreignkey",
    )
    op.create_foreign_key(
        None,
        "event_registration_table_persons",
        "persons",
        ["matched_person_id"],
        ["id"],
        ondelete="SET NULL",
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(
        None, "event_registration_table_persons", type_="foreignkey"
    )
    op.create_foreign_key(
        "event_registration_table_persons_matched_person_id_fkey",
        "event_registration_table_persons",
        "persons",
        ["matched_person_id"],
        ["id"],
        ondelete="CASCADE",
    )
    # ### end Alembic commands ###

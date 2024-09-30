"""Delete some unique constraints

Revision ID: 27eff2af5234
Revises: 7174752ae72c
Create Date: 2024-09-26 22:13:28.840342

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "27eff2af5234"
down_revision: Union[str, None] = "7174752ae72c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(
        "_table_matched_person_uc",
        "event_registration_table_persons",
        type_="unique",
    )
    op.drop_constraint(
        "_protocol_matched_person_uc", "protocol_persons", type_="unique"
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(
        "_protocol_matched_person_uc",
        "protocol_persons",
        ["protocol_id", "matched_person_id"],
    )
    op.create_unique_constraint(
        "_table_matched_person_uc",
        "event_registration_table_persons",
        ["table_id", "matched_person_id"],
    )
    # ### end Alembic commands ###

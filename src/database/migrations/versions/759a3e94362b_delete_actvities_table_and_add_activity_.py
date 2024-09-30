"""delete actvities table and add activity enum 2

Revision ID: 759a3e94362b
Revises: db1027b969f4
Create Date: 2024-07-24 12:20:47.865402

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "759a3e94362b"
down_revision: Union[str, None] = "db1027b969f4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute("DROP TABLE activities CASCADE")
    activity_type = postgresql.ENUM('VK_LIKE', 'VK_COMMENT', name='activity_type')
    activity_type.create(op.get_bind(), checkfirst=True)
    op.add_column(
        "vk_activities",
        sa.Column(
            "activity",
            activity_type,
            nullable=False,
        ),
    )

    op.drop_column("vk_activities", "activity_id")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "vk_activities",
        sa.Column(
            "activity_id", sa.INTEGER(), autoincrement=False, nullable=False
        ),
    )
    op.create_foreign_key(
        "vk_activities_activity_id_fkey",
        "vk_activities",
        "activities",
        ["activity_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.drop_column("vk_activities", "activity")
    op.create_table(
        "activities",
        sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column("name", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.PrimaryKeyConstraint("id", name="activities_pkey"),
        sa.UniqueConstraint("name", name="activities_name_key"),
    )
    # ### end Alembic commands ###
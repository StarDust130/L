"""allow discovered jobs to omit source identifiers and apply URLs"""

from typing import Sequence, Union

from alembic import op


revision: str = "a1c2d3e4f5a6"
down_revision: Union[str, Sequence[str], None] = "fd4d543539b5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("jobs", "external_id", nullable=True)
    op.alter_column("jobs", "apply_url", nullable=True)


def downgrade() -> None:
    op.alter_column("jobs", "apply_url", nullable=False)
    op.alter_column("jobs", "external_id", nullable=False)

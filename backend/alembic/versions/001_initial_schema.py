"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-03-22

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Tables are created via SQLAlchemy metadata on startup for prototype simplicity.
    # This revision exists so Alembic is ready for future incremental migrations.
    pass


def downgrade() -> None:
    pass

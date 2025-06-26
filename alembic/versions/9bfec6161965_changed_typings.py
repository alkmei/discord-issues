"""changed typings

Revision ID: 9bfec6161965
Revises: 68f46830f9ce
Create Date: 2025-06-25 22:37:54.009824

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9bfec6161965'
down_revision: Union[str, Sequence[str], None] = '68f46830f9ce'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

"""Status backpopulate

Revision ID: 071d50848c8d
Revises: 9bfec6161965
Create Date: 2025-06-28 19:25:09.728982

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '071d50848c8d'
down_revision: Union[str, Sequence[str], None] = '9bfec6161965'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

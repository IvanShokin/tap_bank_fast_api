"""add_user_mail_and_phone

Revision ID: 0003
Revises: 0002
Create Date: 2024-11-12 08:54:48.821115

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0003'
down_revision: Union[str, None] = '0002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('phone', sa.String(length=255), nullable=False))
    op.add_column('user', sa.Column('email', sa.String(length=255), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'email')
    op.drop_column('user', 'phone')
    # ### end Alembic commands ###
"""Add system_roles to employees

Revision ID: 20260118_0001
Revises: 20260117_0005_v3_office_employee_hub
Create Date: 2026-01-18

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision = '202601180001'
down_revision = '202601170005'

branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('employees', sa.Column('system_roles', JSONB, nullable=True))


def downgrade() -> None:
    op.drop_column('employees', 'system_roles')

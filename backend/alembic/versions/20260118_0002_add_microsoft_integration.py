"""Add Microsoft 365 integration fields

Revision ID: 20260118_0002
Revises: 20260118_0001_add_employee_system_roles
Create Date: 2026-01-18

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '202601180002'
down_revision = '202601180001'

branch_labels = None
depends_on = None


def upgrade() -> None:
    # Office: teams_group_id and sharepoint_folder_url
    op.add_column('offices', sa.Column('teams_group_id', sa.String(100), nullable=True))
    op.add_column('offices', sa.Column('sharepoint_folder_url', sa.Text(), nullable=True))
    
    # Employee: sharepoint_folder_url
    op.add_column('employees', sa.Column('sharepoint_folder_url', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('employees', 'sharepoint_folder_url')
    op.drop_column('offices', 'sharepoint_folder_url')
    op.drop_column('offices', 'teams_group_id')

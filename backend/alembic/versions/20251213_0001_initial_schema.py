"""Initial schema

Revision ID: 0001
Revises: 
Create Date: 2025-12-13

Creates the initial database schema:
- templates: Document template metadata
- template_versions: Version history for templates
- tags: User-defined labels for templates
- categories: Hierarchical organization of templates
- template_tags: Junction table for template-tag relationships
- template_categories: Junction table for template-category relationships
- audit_logs: Action tracking for compliance
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create tags table
    op.create_table(
        'tags',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('color', sa.String(7), nullable=False, server_default='#3B82F6'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_tags')),
        sa.UniqueConstraint('name', name=op.f('uq_tags_name'))
    )
    op.create_index(op.f('ix_tags_name'), 'tags', ['name'], unique=False)

    # Create categories table
    op.create_table(
        'categories',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('icon', sa.String(50), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_categories')),
        sa.UniqueConstraint('name', name=op.f('uq_categories_name'))
    )
    op.create_index(op.f('ix_categories_name'), 'categories', ['name'], unique=False)
    op.create_index('idx_categories_sort_order', 'categories', ['sort_order'], unique=False)

    # Create templates table
    op.create_table(
        'templates',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('file_name', sa.String(255), nullable=False),
        sa.Column('file_type', sa.String(10), nullable=False),
        sa.Column('file_size_bytes', sa.BigInteger(), nullable=False),
        sa.Column('azure_blob_url', sa.Text(), nullable=False),
        sa.Column('azure_blob_container', sa.String(100), nullable=False, server_default='templates'),
        sa.Column('status', sa.String(20), nullable=False, server_default='draft'),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('created_by', sa.String(255), nullable=False),
        sa.Column('updated_by', sa.String(255), nullable=False),
        sa.Column('preview_url', sa.Text(), nullable=True),
        sa.Column('page_count', sa.Integer(), nullable=True),
        sa.Column('language', sa.String(10), nullable=False, server_default='nb-NO'),
        sa.Column('vitec_merge_fields', postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_templates'))
    )
    op.create_index('idx_templates_status', 'templates', ['status'], unique=False)
    op.create_index('idx_templates_created_at', 'templates', ['created_at'], unique=False)

    # Create template_versions table
    op.create_table(
        'template_versions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('template_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('version_number', sa.Integer(), nullable=False),
        sa.Column('file_name', sa.String(255), nullable=False),
        sa.Column('azure_blob_url', sa.Text(), nullable=False),
        sa.Column('file_size_bytes', sa.BigInteger(), nullable=False),
        sa.Column('created_by', sa.String(255), nullable=False),
        sa.Column('change_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['template_id'], ['templates.id'], name=op.f('fk_template_versions_template_id_templates'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_template_versions'))
    )
    op.create_index('uq_template_version', 'template_versions', ['template_id', 'version_number'], unique=True)

    # Create template_tags junction table
    op.create_table(
        'template_tags',
        sa.Column('template_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tag_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], name=op.f('fk_template_tags_tag_id_tags'), ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['template_id'], ['templates.id'], name=op.f('fk_template_tags_template_id_templates'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('template_id', 'tag_id', name=op.f('pk_template_tags'))
    )

    # Create template_categories junction table
    op.create_table(
        'template_categories',
        sa.Column('template_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('category_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], name=op.f('fk_template_categories_category_id_categories'), ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['template_id'], ['templates.id'], name=op.f('fk_template_categories_template_id_templates'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('template_id', 'category_id', name=op.f('pk_template_categories'))
    )

    # Create audit_logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('entity_type', sa.String(50), nullable=False),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('action', sa.String(50), nullable=False),
        sa.Column('user_email', sa.String(255), nullable=False),
        sa.Column('details', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_audit_logs'))
    )
    op.create_index('idx_audit_logs_entity', 'audit_logs', ['entity_type', 'entity_id'], unique=False)
    op.create_index('idx_audit_logs_user', 'audit_logs', ['user_email'], unique=False)
    op.create_index('idx_audit_logs_action', 'audit_logs', ['action'], unique=False)
    op.create_index(op.f('ix_audit_logs_timestamp'), 'audit_logs', ['timestamp'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order (respecting foreign key constraints)
    op.drop_table('audit_logs')
    op.drop_table('template_categories')
    op.drop_table('template_tags')
    op.drop_table('template_versions')
    op.drop_table('templates')
    op.drop_table('categories')
    op.drop_table('tags')


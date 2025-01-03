"""Add is_admin to users

Revision ID: 6ec1b2ccb082
Revises: 0a5f57588ddb
Create Date: 2024-03-21 01:41:32.192756

"""
from alembic import op, context
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6ec1b2ccb082'
down_revision = '0a5f57588ddb'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Commands auto generated by Alembic - please adjust!
    op.create_table('quizzes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('questions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('quiz_id', sa.Integer(), nullable=True),
    sa.Column('text', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['quiz_id'], ['quizzes.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('options',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('question_id', sa.Integer(), nullable=True),
    sa.Column('text', sa.String(), nullable=False),
    sa.Column('is_correct', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['question_id'], ['questions.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

    # Add is_admin column to users table
    op.add_column('users', sa.Column('is_admin', sa.Boolean(), nullable=True))

    # Conditional execution based on the database dialect
    if not context.config.get_main_option('sqlalchemy.url').startswith('sqlite'):
        op.alter_column('sales', 'product_id',
                   existing_type=sa.INTEGER(),
                   nullable=True)

def downgrade() -> None:
    # Commands auto generated by Alembic - please adjust!
    if not context.config.get_main_option('sqlalchemy.url').startswith('sqlite'):
        op.alter_column('sales', 'product_id',
                   existing_type=sa.INTEGER(),
                   nullable=False)

    op.drop_column('users', 'is_admin')
    op.drop_table('options')
    op.drop_table('questions')
    op.drop_table('quizzes')

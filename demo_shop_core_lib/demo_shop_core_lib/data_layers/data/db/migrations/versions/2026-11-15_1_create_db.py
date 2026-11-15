"""create_db

Revision ID: 1
Revises:
Create Date: 2026-11-15 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

from demo_shop_core_lib.data_layers.data.db.entities.demo_shop import DemoShop

revision = '1'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        DemoShop.__tablename__,
        sa.Column(DemoShop.id.key, sa.Integer, primary_key=True, nullable=False),
        sa.Column(DemoShop.name.key, sa.VARCHAR(length=255), nullable=False),
    )


def downgrade():
    op.drop_table(DemoShop.__tablename__)

from sqlalchemy import Column, INTEGER, VARCHAR

from core_lib.data_layers.data.db.sqlalchemy.base import Base


class DemoShop(Base):

    __tablename__ = 'demo_shop'

    id = Column(INTEGER, primary_key=True, autoincrement=True)
    name = Column(VARCHAR(length=255), nullable=False)

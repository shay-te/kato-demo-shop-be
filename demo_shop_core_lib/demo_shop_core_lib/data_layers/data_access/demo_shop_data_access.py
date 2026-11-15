from core_lib.connection.sql_alchemy_connection_factory import SqlAlchemyConnectionFactory
from core_lib.data_layers.data_access.db.crud.crud import CRUD
from core_lib.data_layers.data_access.db.crud.crud_data_access import CRUDDataAccess
from core_lib.rule_validator.rule_validator import RuleValidator, ValueRuleValidator

from demo_shop_core_lib.data_layers.data.db.entities.demo_shop import DemoShop

# sqlite does not enforce a VARCHAR length, so the length (and non-empty) rule
# lives here. Presence is the column's job (`nullable=False`).
allowed_update_types = [
    ValueRuleValidator(
        DemoShop.name.key,
        str,
        custom_validator=lambda name: bool(name) and len(name) <= 255,
    ),
]
rule_validator = RuleValidator(allowed_update_types)


class DemoShopDataAccess(CRUDDataAccess):

    def __init__(self, db: SqlAlchemyConnectionFactory):
        CRUD.__init__(self, DemoShop, db, rule_validator)

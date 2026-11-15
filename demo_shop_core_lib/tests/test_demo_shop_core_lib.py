import unittest

from sqlalchemy import inspect, select

from core_lib.core_lib import CoreLib
from demo_shop_core_lib.data_layers.data.db.entities.demo_shop import DemoShop
from demo_shop_core_lib.data_layers.service.demo_shop_service import DemoShopService
from demo_shop_core_lib.demo_shop_core_lib import DemoShopCoreLib
from tests.test_data.helpers.util import load_config, sync_create_start_core_lib


class TestDemoShopCoreLib(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.demo_shop_core_lib = sync_create_start_core_lib()

    def test_builds_from_the_hydra_config(self):
        self.assertIsInstance(self.demo_shop_core_lib, DemoShopCoreLib)
        self.assertIsInstance(self.demo_shop_core_lib.demo_shop, DemoShopService)

    def test_config_merges_the_packaged_yaml_with_the_test_override(self):
        config = load_config()
        # from the packaged demo_shop_core_lib.yaml
        self.assertEqual('demo_shop_alembic_version', config.core_lib.alembic.version_table)
        self.assertEqual('sqlite', config.core_lib.data.sqlalchemy.config.url.protocol)
        # from the test override (the packaged value is a file)
        self.assertEqual(':memory:', config.core_lib.data.sqlalchemy.config.url.file)

    def test_package_exports_the_main_class_and_version(self):
        import demo_shop_core_lib
        self.assertIs(DemoShopCoreLib, demo_shop_core_lib.DemoShopCoreLib)
        self.assertEqual('0.0.0.1', demo_shop_core_lib.__version__)

    def test_public_surface_is_the_service_only(self):
        public = {name for name in vars(self.demo_shop_core_lib) if not name.startswith('_')}
        self.assertEqual({'config', 'demo_shop'}, public)

    def test_a_second_instance_in_one_process_shares_the_database(self):
        second = DemoShopCoreLib(load_config())  # guarded registrations: must not raise
        created = self.demo_shop_core_lib.demo_shop.create('acme-shared')
        self.assertEqual(created, second.demo_shop.get(created[DemoShop.id.key]))

    def test_service_writes_reach_a_real_sqlite_table(self):
        engine = CoreLib.connection_factory_registry.get_or_reg(load_config().core_lib.data.sqlalchemy).engine
        self.assertEqual('sqlite', engine.dialect.name)
        self.assertIn(DemoShop.__tablename__, inspect(engine).get_table_names())

        created = self.demo_shop_core_lib.demo_shop.create('acme-row')
        with engine.connect() as connection:
            row = connection.execute(
                select(DemoShop.__table__).where(DemoShop.id == created[DemoShop.id.key])).mappings().one()
        self.assertEqual('acme-row', row[DemoShop.name.key])

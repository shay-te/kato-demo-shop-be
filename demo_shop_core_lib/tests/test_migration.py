import copy
import glob
import inspect as python_inspect
import os
import tempfile
import unittest

from sqlalchemy import create_engine, inspect, text

from core_lib.data_layers.data.db.sqlalchemy.base import Base
from demo_shop_core_lib.data_layers.data.db.entities.demo_shop import DemoShop
from demo_shop_core_lib.demo_shop_core_lib import DemoShopCoreLib
from tests.test_data.helpers.util import load_config

MIGRATIONS_DIR = os.path.join(
    os.path.dirname(python_inspect.getfile(DemoShopCoreLib)), 'data_layers', 'data', 'db', 'migrations')


def _schema(engine) -> dict:
    inspector = inspect(engine)
    schema = {}
    for table in inspector.get_table_names():
        schema[table] = {
            'columns': [(column['name'], str(column['type']), column['nullable'], column['default'])
                        for column in inspector.get_columns(table)],
            'primary_key': inspector.get_pk_constraint(table)['constrained_columns'],
            'indexes': sorted((index['name'], tuple(index['column_names']), bool(index['unique']))
                              for index in inspector.get_indexes(table)),
            'unique': sorted(tuple(unique['column_names']) for unique in inspector.get_unique_constraints(table)),
            'foreign_keys': inspector.get_foreign_keys(table),
        }
    return schema


class TestMigration(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)

    def _config_for(self, file_name: str):
        # Alembic writes into the config node it is given, so never hand it the shared one.
        config = copy.deepcopy(load_config())
        url = config.core_lib.data.sqlalchemy.config.url
        # build_url strips a leading '/', so an absolute path must go in relative
        url.file = os.path.relpath(os.path.join(self._tmp.name, file_name))
        return config

    def _engine(self, file_name: str):
        engine = create_engine('sqlite:///{}'.format(os.path.join(self._tmp.name, file_name)))
        self.addCleanup(engine.dispose)
        return engine

    def test_install_produces_the_same_schema_as_create_all(self):
        DemoShopCoreLib.install(self._config_for('migrated.db'))

        created_engine = self._engine('created.db')
        Base.metadata.create_all(created_engine)

        migrated = _schema(self._engine('migrated.db'))
        version_table = migrated.pop(load_config().core_lib.alembic.version_table)
        self.assertEqual(['version_num'], [column[0] for column in version_table['columns']])
        self.assertEqual(_schema(created_engine), migrated)
        self.assertIn(DemoShop.__tablename__, migrated)

    def test_install_records_revision_one_in_the_library_version_table(self):
        DemoShopCoreLib.install(self._config_for('migrated.db'))
        DemoShopCoreLib.install(self._config_for('migrated.db'))  # second run is a no-op

        version_table = load_config().core_lib.alembic.version_table
        with self._engine('migrated.db').connect() as connection:
            versions = connection.execute(text('SELECT version_num FROM {}'.format(version_table))).scalars().all()
        self.assertEqual(['1'], versions)

    def test_uninstall_drops_the_table(self):
        DemoShopCoreLib.install(self._config_for('migrated.db'))
        DemoShopCoreLib.uninstall(self._config_for('migrated.db'))

        self.assertNotIn(DemoShop.__tablename__, inspect(self._engine('migrated.db')).get_table_names())

    def test_exactly_one_migration_and_migration_ver_matches(self):
        migrations = [path for path in glob.glob(os.path.join(MIGRATIONS_DIR, 'versions', '*.py'))
                      if not path.endswith('__init__.py')]
        self.assertEqual(['2026-11-15_1_create_db.py'], [os.path.basename(path) for path in migrations])
        with open(os.path.join(MIGRATIONS_DIR, '.migration_ver')) as file:
            self.assertEqual('1', file.read().strip())

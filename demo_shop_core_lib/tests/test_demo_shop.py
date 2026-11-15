import unittest

from sqlalchemy.exc import IntegrityError

from demo_shop_core_lib.data_layers.data.db.entities.demo_shop import DemoShop
from tests.test_data.helpers.util import sync_create_start_core_lib

ABSENT_DEMO_SHOP_ID = 2_000_000_000  # far above any autoincrement


class TestDemoShop(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.demo_shop_core_lib = sync_create_start_core_lib()

    def test_create_get_update_delete_round_trip(self):
        created = self.demo_shop_core_lib.demo_shop.create('acme')
        demo_shop_id = created[DemoShop.id.key]
        self.assertIsInstance(demo_shop_id, int)
        self.assertEqual({DemoShop.id.key: demo_shop_id, DemoShop.name.key: 'acme'}, created)

        # get is cached: the first read fills the cache, the update must evict it
        self.assertEqual({DemoShop.id.key: demo_shop_id, DemoShop.name.key: 'acme'},
                         self.demo_shop_core_lib.demo_shop.get(demo_shop_id))

        self.demo_shop_core_lib.demo_shop.update(demo_shop_id, {DemoShop.name.key: 'acme-widget'})
        self.assertEqual({DemoShop.id.key: demo_shop_id, DemoShop.name.key: 'acme-widget'},
                         self.demo_shop_core_lib.demo_shop.get(demo_shop_id))

        self.assertEqual(1, self.demo_shop_core_lib.demo_shop.delete(demo_shop_id))
        self.assertIsNone(self.demo_shop_core_lib.demo_shop.get(demo_shop_id))
        self.assertEqual(0, self.demo_shop_core_lib.demo_shop.delete(demo_shop_id))

    def test_ids_are_issued_in_increasing_order(self):
        first = self.demo_shop_core_lib.demo_shop.create('acme-1')
        second = self.demo_shop_core_lib.demo_shop.create('acme-2')
        self.assertGreater(second[DemoShop.id.key], first[DemoShop.id.key])

    def test_get_absent_returns_none_every_time(self):
        self.assertIsNone(self.demo_shop_core_lib.demo_shop.get(ABSENT_DEMO_SHOP_ID))
        self.assertIsNone(self.demo_shop_core_lib.demo_shop.get(ABSENT_DEMO_SHOP_ID))

    def test_update_touches_only_its_own_row(self):
        target = self.demo_shop_core_lib.demo_shop.create('acme-target')
        bystander = self.demo_shop_core_lib.demo_shop.create('acme-bystander')
        self.demo_shop_core_lib.demo_shop.get(bystander[DemoShop.id.key])  # warm the cache

        self.demo_shop_core_lib.demo_shop.update(target[DemoShop.id.key], {DemoShop.name.key: 'renamed'})

        self.assertEqual('renamed', self.demo_shop_core_lib.demo_shop.get(target[DemoShop.id.key])[DemoShop.name.key])
        self.assertEqual('acme-bystander',
                         self.demo_shop_core_lib.demo_shop.get(bystander[DemoShop.id.key])[DemoShop.name.key])

    def test_delete_removes_only_its_own_row(self):
        doomed = self.demo_shop_core_lib.demo_shop.create('acme-doomed')
        survivor = self.demo_shop_core_lib.demo_shop.create('acme-survivor')

        self.assertEqual(1, self.demo_shop_core_lib.demo_shop.delete(doomed[DemoShop.id.key]))

        self.assertIsNone(self.demo_shop_core_lib.demo_shop.get(doomed[DemoShop.id.key]))
        self.assertEqual(survivor, self.demo_shop_core_lib.demo_shop.get(survivor[DemoShop.id.key]))

    def test_delete_absent_returns_zero(self):
        self.assertEqual(0, self.demo_shop_core_lib.demo_shop.delete(ABSENT_DEMO_SHOP_ID))

    def test_update_absent_creates_nothing(self):
        self.demo_shop_core_lib.demo_shop.update(ABSENT_DEMO_SHOP_ID, {DemoShop.name.key: 'ghost'})
        self.assertIsNone(self.demo_shop_core_lib.demo_shop.get(ABSENT_DEMO_SHOP_ID))

    def test_update_rejects_a_key_without_a_rule_and_leaves_the_row_untouched(self):
        created = self.demo_shop_core_lib.demo_shop.create('acme')
        demo_shop_id = created[DemoShop.id.key]

        with self.assertRaises(PermissionError):
            self.demo_shop_core_lib.demo_shop.update(demo_shop_id, {'unknown_column': 'x'})
        with self.assertRaises(PermissionError):
            self.demo_shop_core_lib.demo_shop.update(demo_shop_id, {DemoShop.id.key: ABSENT_DEMO_SHOP_ID})

        self.assertEqual(created, self.demo_shop_core_lib.demo_shop.get(demo_shop_id))
        self.assertIsNone(self.demo_shop_core_lib.demo_shop.get(ABSENT_DEMO_SHOP_ID))

    def test_name_at_the_column_limit_round_trips(self):
        longest = 'w' * 255
        created = self.demo_shop_core_lib.demo_shop.create(longest)
        self.assertEqual(longest, self.demo_shop_core_lib.demo_shop.get(created[DemoShop.id.key])[DemoShop.name.key])

    def test_name_one_over_the_limit_is_rejected_on_create_and_update(self):
        too_long = 'w' * 256
        with self.assertRaises(PermissionError):
            self.demo_shop_core_lib.demo_shop.create(too_long)

        created = self.demo_shop_core_lib.demo_shop.create('acme')
        with self.assertRaises(PermissionError):
            self.demo_shop_core_lib.demo_shop.update(created[DemoShop.id.key], {DemoShop.name.key: too_long})
        self.assertEqual('acme', self.demo_shop_core_lib.demo_shop.get(created[DemoShop.id.key])[DemoShop.name.key])

    def test_empty_name_is_rejected_on_create_and_update(self):
        with self.assertRaises(PermissionError):
            self.demo_shop_core_lib.demo_shop.create('')

        created = self.demo_shop_core_lib.demo_shop.create('acme')
        with self.assertRaises(PermissionError):
            self.demo_shop_core_lib.demo_shop.update(created[DemoShop.id.key], {DemoShop.name.key: ''})
        self.assertEqual('acme', self.demo_shop_core_lib.demo_shop.get(created[DemoShop.id.key])[DemoShop.name.key])

    def test_null_name_is_refused_by_the_database(self):
        with self.assertRaises(IntegrityError):
            self.demo_shop_core_lib.demo_shop.create(None)

        created = self.demo_shop_core_lib.demo_shop.create('acme')
        with self.assertRaises(IntegrityError):
            self.demo_shop_core_lib.demo_shop.update(created[DemoShop.id.key], {DemoShop.name.key: None})
        self.assertEqual('acme', self.demo_shop_core_lib.demo_shop.get(created[DemoShop.id.key])[DemoShop.name.key])

    def test_unicode_name_round_trips(self):
        created = self.demo_shop_core_lib.demo_shop.create('ácmé ウィジェット')
        self.assertEqual('ácmé ウィジェット',
                         self.demo_shop_core_lib.demo_shop.get(created[DemoShop.id.key])[DemoShop.name.key])

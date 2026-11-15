import unittest
from http import HTTPStatus

from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils
from demo_shop_core_lib import DemoShopCoreLib
from demo_shop_core_lib.data_layers.data.db.entities.demo_shop import DemoShop

from demo_shop_api.app import create_app
from demo_shop_api.demo_shop_core_lib_instance import DemoShopCoreLibInstance

# A temporary in-memory database with tables from create_all, so the test
# touches no file. The whole url is overridden.
TEST_DB_OVERRIDES = [
    'core_lib.data.sqlalchemy.config.create_db=true',
    'core_lib.data.sqlalchemy.config.url.protocol=sqlite',
    "core_lib.data.sqlalchemy.config.url.file=':memory:'",
]


class TestApp(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = create_app(TEST_DB_OVERRIDES)
        cls.client = cls.app.test_client()

    def test_health_returns_ok(self):
        response = self.client.get('/health')
        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertEqual('application/json', response.mimetype)
        self.assertEqual({'status': 'ok'}, response.get_json())

    def test_health_is_the_only_route(self):
        routes = {rule.rule for rule in self.app.url_map.iter_rules() if rule.endpoint != 'static'}
        self.assertEqual({'/health'}, routes)

    def test_health_refuses_other_methods(self):
        self.assertEqual(HTTPStatus.METHOD_NOT_ALLOWED, self.client.post('/health').status_code)

    def test_unknown_path_is_not_found(self):
        self.assertEqual(HTTPStatus.NOT_FOUND, self.client.get('/missing').status_code)

    def test_web_helpers_use_flask(self):
        self.assertIs(WebHelpersUtils.ServerType.FLASK, WebHelpersUtils.get_server_type())

    def test_core_lib_instance_is_a_working_demo_shop_core_lib(self):
        demo_shop_core_lib = DemoShopCoreLibInstance.get()
        self.assertIsInstance(demo_shop_core_lib, DemoShopCoreLib)

        created = demo_shop_core_lib.demo_shop.create('acme')
        self.assertEqual({DemoShop.id.key: created[DemoShop.id.key], DemoShop.name.key: 'acme'},
                         demo_shop_core_lib.demo_shop.get(created[DemoShop.id.key]))

    def test_a_second_create_app_keeps_the_same_core_lib(self):
        first = DemoShopCoreLibInstance.get()
        create_app(TEST_DB_OVERRIDES)
        self.assertIs(first, DemoShopCoreLibInstance.get())

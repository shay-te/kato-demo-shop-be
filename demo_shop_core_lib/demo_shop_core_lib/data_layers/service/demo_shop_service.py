from http import HTTPStatus

from core_lib.cache.cache_decorator import Cache
from core_lib.data_layers.service.service import Service
from core_lib.data_transform.result_to_dict import ResultToDict
from core_lib.error_handling.status_code_exception import StatusCodeException

from demo_shop_core_lib.constants import DEMO_SHOP_CORE_LIB_CACHE
from demo_shop_core_lib.data_layers.data.db.entities.demo_shop import DemoShop
from demo_shop_core_lib.data_layers.data_access.demo_shop_data_access import DemoShopDataAccess

CACHE_KEY_DEMO_SHOP = 'demo_shop_demo_shop_{demo_shop_id}'


class DemoShopService(Service):

    def __init__(self, demo_shop_da: DemoShopDataAccess):
        self._demo_shop_da = demo_shop_da

    @ResultToDict()
    def create(self, name: str):
        return self._demo_shop_da.create({DemoShop.name.key: name})

    @Cache(CACHE_KEY_DEMO_SHOP, handler_name=DEMO_SHOP_CORE_LIB_CACHE)
    @ResultToDict()
    def get(self, demo_shop_id: int):
        try:
            return self._demo_shop_da.get(demo_shop_id)
        except StatusCodeException as missing:
            if missing.status_code != HTTPStatus.NOT_FOUND:
                raise
            return None

    @Cache(CACHE_KEY_DEMO_SHOP, handler_name=DEMO_SHOP_CORE_LIB_CACHE, invalidate=True)
    def update(self, demo_shop_id: int, data: dict):
        return self._demo_shop_da.update(demo_shop_id, data)

    @Cache(CACHE_KEY_DEMO_SHOP, handler_name=DEMO_SHOP_CORE_LIB_CACHE, invalidate=True)
    def delete(self, demo_shop_id: int) -> int:
        return self._demo_shop_da.delete(demo_shop_id)

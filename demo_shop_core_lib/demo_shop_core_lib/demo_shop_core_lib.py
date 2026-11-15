import inspect
import os

from omegaconf import DictConfig

from core_lib.alembic.alembic import Alembic
from core_lib.cache.cache_handler_ram import CacheHandlerRam
from core_lib.core_lib import CoreLib

from demo_shop_core_lib.constants import DEMO_SHOP_CORE_LIB_CACHE
from demo_shop_core_lib.data_layers.data_access.demo_shop_data_access import DemoShopDataAccess
from demo_shop_core_lib.data_layers.service.demo_shop_service import DemoShopService


class DemoShopCoreLib(CoreLib):
    def __init__(self, conf: DictConfig):
        super().__init__()
        self.config = conf

        if not CoreLib.cache_registry.get(DEMO_SHOP_CORE_LIB_CACHE):
            CoreLib.cache_registry.register(DEMO_SHOP_CORE_LIB_CACHE, CacheHandlerRam())

        core_cfg = conf.core_lib
        db = CoreLib.connection_factory_registry.get_or_reg(core_cfg.data.sqlalchemy)

        self._demo_shop_da = DemoShopDataAccess(db)
        self.demo_shop = DemoShopService(self._demo_shop_da)

    @staticmethod
    def install(cfg: DictConfig):
        Alembic(os.path.dirname(inspect.getfile(DemoShopCoreLib)), cfg).upgrade()

    @staticmethod
    def uninstall(cfg: DictConfig):
        Alembic(os.path.dirname(inspect.getfile(DemoShopCoreLib)), cfg).downgrade()

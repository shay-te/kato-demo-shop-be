import os
import threading
import traceback

import hydra
from hydra.core.global_hydra import GlobalHydra

from core_lib.core_lib import CoreLib
from demo_shop_core_lib.demo_shop_core_lib import DemoShopCoreLib


class DemoShopInstance(object):
    instance = None
    config = None


threadLock = threading.Lock()


def load_config():
    if not DemoShopInstance.config:
        GlobalHydra.instance().clear()
        # relative to this file: tests/test_data/helpers -> tests/test_data/test_config
        hydra.initialize(config_path=os.path.join('..', 'test_config'), caller_stack_depth=1, version_base='1.3')
        DemoShopInstance.config = hydra.compose('config.yaml')
    return DemoShopInstance.config


def sync_create_start_core_lib() -> DemoShopCoreLib:
    threadLock.acquire()
    try:
        if not DemoShopInstance.instance:
            [CoreLib.cache_registry.unregister(key) for key in CoreLib.cache_registry.registered()]
            [CoreLib.observer_registry.unregister(key) for key in CoreLib.observer_registry.registered()]
            DemoShopInstance.instance = DemoShopCoreLib(load_config())
            DemoShopInstance.instance.start_core_lib()

        # Clear the cache
        for key in CoreLib.cache_registry.registered():
            CoreLib.cache_registry.get(key).flush_all()
    except BaseException as e:
        print(''.join(traceback.format_exception(type(e), e, e.__traceback__)))
        raise e
    finally:
        threadLock.release()
    return DemoShopInstance.instance

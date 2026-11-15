from demo_shop_core_lib import DemoShopCoreLib


class DemoShopCoreLibInstance(object):
    """The app's one DemoShopCoreLib per process. The singleton is the host's
    choice, so it lives here, not in the library."""

    _app_instance = None

    @staticmethod
    def init(core_lib_cfg):
        if not DemoShopCoreLibInstance._app_instance:
            DemoShopCoreLibInstance._app_instance = DemoShopCoreLib(core_lib_cfg)
            DemoShopCoreLibInstance._app_instance.start_core_lib()

    @staticmethod
    def get() -> DemoShopCoreLib:
        return DemoShopCoreLibInstance._app_instance

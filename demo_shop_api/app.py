import os

import hydra
from flask import Flask
from hydra.core.global_hydra import GlobalHydra
from omegaconf import DictConfig

from core_lib.web_helpers.request_response_helpers import response_json
from core_lib.web_helpers.web_helprs_utils import WebHelpersUtils

from demo_shop_api.demo_shop_core_lib_instance import DemoShopCoreLibInstance

CONFIG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config')


def compose_config(overrides: list = None) -> DictConfig:
    GlobalHydra.instance().clear()
    with hydra.initialize_config_dir(config_dir=CONFIG_DIR, version_base='1.3'):
        return hydra.compose('config', overrides=overrides or [])


def create_app(config_overrides: list = None) -> Flask:
    DemoShopCoreLibInstance.init(compose_config(config_overrides))
    WebHelpersUtils.init(WebHelpersUtils.ServerType.FLASK)

    app = Flask(__name__)

    @app.get('/health')
    def health():
        return response_json({'status': 'ok'})

    return app

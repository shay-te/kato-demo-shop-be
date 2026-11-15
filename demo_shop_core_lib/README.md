# DemoShopCoreLib
DemoShopCoreLib is built using [Core-Lib](https://github.com/shay-te/core-lib).

## Example

Run from this directory (it holds `core_lib_config.yaml`):

```python
import os

import hydra
from hydra.core.global_hydra import GlobalHydra

from demo_shop_core_lib import DemoShopCoreLib
from demo_shop_core_lib.data_layers.data.db.entities.demo_shop import DemoShop

GlobalHydra.instance().clear()
with hydra.initialize_config_dir(config_dir=os.getcwd(), version_base='1.3'):
    # `demo_shop_core_lib` is found through the library's Hydra search-path plugin
    config = hydra.compose('core_lib_config.yaml')  # defaults: core_lib, demo_shop_core_lib

DemoShopCoreLib.install(config)  # applies the Alembic migration
demo_shop_core_lib = DemoShopCoreLib(config)

created = demo_shop_core_lib.demo_shop.create('acme')
demo_shop_core_lib.demo_shop.update(created[DemoShop.id.key], {DemoShop.name.key: 'acme-widget'})
demo_shop_core_lib.demo_shop.get(created[DemoShop.id.key])
demo_shop_core_lib.demo_shop.delete(created[DemoShop.id.key])
```

## Tests

From this directory:

```bash
python -P -m unittest discover -s tests -t .
```

## License
MIT, see [LICENSE](LICENSE).

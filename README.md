# kato-demo-shop-be

Demo shop backend: `demo_shop_core_lib` (a library built on
[core-lib](https://github.com/shay-te/core-lib)) and `demo_shop_api`, a minimal
Flask app that uses it. The database is sqlite, so no database server is needed.

```
kato-demo-shop-be/
  demo_shop_core_lib/   the library (+ its own tests)
  demo_shop_api/        the Flask app (+ its own tests)
  requirements.txt
```

## Install

Requires Python 3.11 and the `core-lib` repository checked out beside this one
(`../core-lib`). Run everything from this directory.

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install --no-build-isolation -r requirements.txt
```

`--no-build-isolation` is needed because core-lib's `setup.py` imports pip.

## Run

```bash
flask --app demo_shop_api.app run
curl http://127.0.0.1:5000/health        # {"status": "ok"}
```

The library stores its data in `demo_shop.db` in the working directory. To create
its table, apply the migration once:

```bash
python -c "from demo_shop_api.app import compose_config; from demo_shop_core_lib import DemoShopCoreLib; DemoShopCoreLib.install(compose_config())"
```

## Test

```bash
(cd demo_shop_core_lib && PYTHONPATH=. python -P -m unittest discover -s tests -t .) && PYTHONPATH=. python -P -m unittest discover -s demo_shop_api/tests -t .
```

The two packages run in separate processes because each has its own `tests`
package. `PYTHONPATH=.` puts this repo's `tests` ahead of core-lib's.

## License

MIT, see [LICENSE](LICENSE).

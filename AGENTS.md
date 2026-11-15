# AGENTS Notes — kato-demo-shop-be

The backend rules live in two places; this file does not repeat them:

| Read | For |
|---|---|
| [`demo_shop_core_lib/AGENTS.md`](demo_shop_core_lib/AGENTS.md) | The library: its specific notes and helper map. |
| [`../core-lib/AGENTS.md`](../core-lib/AGENTS.md) | The core-lib rulebook every `*-core-lib` follows, and the mandatory skill routing table (`../core-lib/skills/`). |

Layout:

- `demo_shop_core_lib/` — the library (entities, DataAccess, services, migrations). Host-agnostic: no Flask, no app names.
- `demo_shop_api/` — the Flask app (the host). It composes the Hydra config, owns the `DemoShopCoreLibInstance` singleton and picks the web server type.

How to install, run and test: [`README.md`](README.md).

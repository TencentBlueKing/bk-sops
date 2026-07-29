# Plugin Gateway Catalog Source Filter Plan

Spec: `docs/specs/2026-07-20-plugin-gateway-catalog-source-filter-design.md`

1. Add tests proving built-in requests do not load third-party metadata and
   third-party requests do not load the built-in catalog.
2. Pass `plugin_source` into the catalog builder and select the required source
   before any source-specific loading begins.
3. Run `gcloud.tests.plugin_gateway.test_catalog` and inspect the final diff.

Test command:

```bash
set -a
source /Users/dengyh/Projects/bk-sops/.env
set +a
PYENV_VERSION=3.6.15 python manage.py test gcloud.tests.plugin_gateway.test_catalog -v 2
```

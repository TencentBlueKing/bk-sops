# Plugin Gateway Declarative Form Controls Implementation Plan

> **Goal:** Safely expose high-value built-in plugin form semantics through the existing `uniform_api v4.0.0` detail response without transporting or executing legacy JavaScript.

## Task 1: Define and test built-in form overrides

**Files:**
- Create: `gcloud/plugin_gateway/services/builtin_form_schema.py`
- Test: `gcloud/tests/plugin_gateway/test_builtin_form_schema.py`

1. Add failing tests for top-level `codeEditor`, top-level `textarea`, and nested table `password` overrides.
2. Add a declarative `(component_code, field_path)` override registry.
3. Build a JSON-safe `form_schema` from normalized component inputs and apply overrides recursively.
4. Keep components without an explicit override on the existing flat-input compatibility path.

Run:

```bash
python manage.py test gcloud.tests.plugin_gateway.test_builtin_form_schema -v 2
```

## Task 2: Expose the schema through the built-in catalog

**Files:**
- Modify: `gcloud/plugin_gateway/services/builtin_catalog.py`
- Modify: `gcloud/plugin_gateway/services/catalog.py`
- Modify: `gcloud/tests/plugin_gateway/test_builtin_catalog.py`
- Modify: `gcloud/tests/plugin_gateway/test_catalog.py`

1. Add failing catalog tests for `form_schema` on JOB detail responses.
2. Attach the generated schema to built-in plugin details.
3. Preserve the field through the unified catalog detail response.
4. Confirm plugins without overrides still return their existing `inputs` contract.

## Task 3: Document and package the protocol extension

**Files:**
- Modify: `docs/specs/2026-06-26-plugin-gateway-full-capability-design.md`
- Modify: `docs/zh_hans/apidoc/plugin_gateway_get_plugin_detail.md`
- Modify: `docs/en/apidoc/plugin_gateway_get_plugin_detail.md`
- Regenerate: `gcloud/apigw/docs/apigw-docs.tgz`

Document the supported declarative controls and the deferred dynamic-control boundary, then run the focused plugin-gateway test suite and APIGW archive verification.

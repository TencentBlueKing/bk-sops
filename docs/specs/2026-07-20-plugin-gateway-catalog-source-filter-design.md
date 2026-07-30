# Plugin Gateway Catalog Source Filter Design

## Goal

Reduce plugin list latency when a consumer requests only one plugin source.

## Decision

`GET plugin-gateway/plugins/` reads the optional `plugin_source` query parameter
before building the catalog:

- `builtin`: load only the built-in catalog.
- `third_party`: load only the third-party catalog and metadata.
- missing or unknown: preserve the existing behavior and load both catalogs.

The existing category, keyword, blacklist, URL generation, and response shape
remain unchanged. Plugin detail and execution behavior are outside this change.

## Compatibility

Requests without `plugin_source` still receive the full catalog. Unknown source
values still produce an empty filtered result after loading the full catalog,
matching the current API behavior.

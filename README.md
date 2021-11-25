# ![](https://github.com/sourceplusplus/live-platform/blob/master/.github/media/sourcepp_logo.svg)

[![License](https://img.shields.io/github/license/sourceplusplus/probe-python)](LICENSE)
![GitHub release](https://img.shields.io/github/v/release/sourceplusplus/probe-python?include_prereleases)
[![E2E](https://github.com/sourceplusplus/probe-python/actions/workflows/e2e.yml/badge.svg)](https://github.com/sourceplusplus/probe-python/actions/workflows/e2e.yml)

# What is this?

This project provides Python support to the [Source++](https://github.com/sourceplusplus/live-platform) open-source live coding platform.

# Usage

- `pip install sourceplusplus`

## Attach

```python
from sourceplusplus.SourcePlusPlus import SourcePlusPlus
SourcePlusPlus().attach()
```

### Config

Use `spp-probe.yml` file in working directory (or use `SPP_PROBE_CONFIG_FILE` env):

```yml
spp:
  platform_host: "localhost"
  disable_tls: true
skywalking:
  collector:
    backend_service: "localhost:11800"
```

Or construct with dict:

```python
from sourceplusplus.SourcePlusPlus import SourcePlusPlus
SourcePlusPlus({
    "spp.platform_host": "localhost",
    "spp.disable_tls": True,
    "skywalking.collector.backend_service": "localhost:11800"
}).attach()
```

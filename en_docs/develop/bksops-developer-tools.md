## Introduction

In the process of developing SOPS plugins, in addition to writing the logic of the plugin itself, developers need to spend much time on "static file collection", "project restart" and "celery worker restart". This SOPS developer toolkit uses django and djcelery patches to implement **automatic static file collection, automatic project restart, and worker automatic restart after plugin code modification** without the need to explicitly modify the project source code. This allows SOPS plugin developers to concentrate on the plugin design and improves the plugin development efficiency.

## Installation

Add envionment variable `USE_AUTO_PATCH=True`

Add the following content in `local_settings.py`:

```python
from scripts.auto_reload_tools.auth_collectstatic_patch import patch_django_autoreload
from scripts.auto_reload_tools.auto_reload_worker import patch_worker_autoreload

# static file js file change project automatic collect static files + project restart
patch_django_autoreload()
# When files in the monitored plugin directory are changed, the worker will completed restart automatically.
patch_worker_autoreload()
```

## Notes:

- Before using `patch_django_autoreload`, please make sure that the directory for plugin static file development is: `pipeline_plugins//components//static`. If you write `js` in the project root directory, please copy the `js` file into `pipeline_plugins//components//static` manually. **Please use this feature with caution**. Or it may accidentally overwrite the `js` file in `static` with the file in `pipeline_plugins//components//static`.
- Currently, `patch_worker_autoreload` will **automatically restart worker when it detects plugin code changes**. This feature is very useful when you are developing plugins locally. **However, when there is a task running, the restart will not be delayed** (This option might be added later). **As for now, this plugin can be used in most scenarios.**
- `Monkey patches can be very dangerous for a project, unless your are fully aware of what those patches do.` This toolkit should be only used to improve the efficiency when developing plugins locally. Please don't use them in production environment!


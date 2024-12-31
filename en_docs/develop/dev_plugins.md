# Standard plugin development

## About standard plugins
Refer to [About standard plugins](../features/plugin_usage.md)

## Standard plugin development procedure

### 1. Initialize plugin module
Execute `python manage.py create_atoms_app {CUSTOM PLUGINS NAME}` under project root directory, where `{CUSTOM PLUGINS NAME}` is the standard plugin pack name you are developing.
Please be careful not to use the same name with existing modules and plugin packs. The name should reflect the function of the plugin pack. After command execution, the following directory structure will be generated:
```
{CUSTOM PLUGINS NAME}
├── __init__.py
├── apps.py
├── components
│   ├── __init__.py
│   └── collections
│       ├── __init__.py
│       └── plugins.py
├── migrations
│   └── __init__.py
├── static
│   └── {CUSTOM PLUGINS NAME}
│       └── plugins.js
└── tests
    ├── __init__.py
    └── components
        ├── __init__.py
        └── collections
            ├── __init__.py
            └── plugins_test
                └── __init__.py
```
In the above directory structure, standard plugin pack background code files are placed in `components` directory, standard plugin pack frontend static code files are placed in `static` directory. `plugin.py` and `plugin.js` can be renamed according to
the system name abbreviation you are developing the standard plugin for, such as job, cmdb, etc.


### 2. Modify project settings configuration
Open `config/default.py`, find the INSTALLED_APPS variable, and add the `{CUSTOM PLUGINS NAME}` you created in step 1.


### 3. Add a new API gateway
If the standard plugin you are developing uses a custom API gateway, after you connect the interface to the Blueking API gateway, you need to manually add the API to the Client SDK.
Write the following code in the `{CUSTOM PLUGINS NAME}/__init__.py` file to add the corresponding interface to the Client:

```python
from packages.blueking.component import collections
from packages.blueking.component.base import ComponentAPI
from packages.blueking.component.client import ComponentClient

class CollectionsMySystem(object):

    def __init__(self, client):
        self.client = client
    
        self.get_status = ComponentAPI(
            client=self.client, method='GET',
            path='/api/c/compapi{bk_api_ver}/my_system/status/',
            description=u"Get Status"
        )

        self.set_status = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/my_system/status/',
            description=u"Set Status"
        )


collections.AVAILABLE_COLLECTIONS.update({
    'my_system': CollectionsMySystem
})

ComponentClient.setup_components(collections.AVAILABLE_COLLECTIONS)

```

In the above example, a system named `my_system` is added to the Client, and two interfaces, `get_status` and `set_status`, are added to the system.


### 4. Standard plugin background development

#### Generate standard plugin base files and directories
Execute the command in the project root directory
```shell script
python manage.py create_new_plugin {group_code} {plugin_code} {version} {plugin_env} {app_code} {append}
```

where

- **group_code** is the series to which the plugin belongs (e.g. cc, tgw, gcs)
- **plugin_code** is the code of the plugin (e.g. create_set)
- **version**is the version of the plugin (e.g. v1.0)
- **plugin_env** is the type of plugin (e.g. open, ieod)
- **app_code** is the code of the app where the plugin is located (e.g. pipeline_plugins)
- **append** is the end of the directory where the plugin is located (e.g. the sites in pipeline_plugins/components/collections/sites. Can be empty)

eg.
```shell script
python manage.py create_new_plugin cc create_set v1.0 open pipeline_plugins sites
```
In the above example, we are creating CC-series plugin called create_set. Its version number is v1.0 and is an open source plugin.

Write plugin background logic in `plugin.py`. It mainly includes standard plugin definitions and background execution logic. A sample code is given below.

```python
# -*- coding: utf-8 -*-

import logging

from django.utils.translation import gettext_lazy as _

from pipeline.core.flow.activity import Service
from pipeline.component_framework.component import Component
from gcloud.conf import settings

logger = logging.getLogger('celery')
get_client_by_user = settings.ESB_GET_CLIENT_BY_USER

__group_name__ = _(u"CustomPlugin(CUSTOM)")


class TestCustomService(Service):
    __need_schedule__ = False

    def execute_pre_process(self, data, parent_data):
        test_input = data.inputs.test_input
        if not test_input.startswith("test_"):
            message = "test_input should start with 'test_'"
            data.set_outputs('ex_data', message)
            return False
        return True
        
    def execute(self, data, parent_data):
        executor = parent_data.inputs.executor
        biz_cc_id = parent_data.inputs.biz_cc_id
        client = get_client_by_user(executor)

        test_input = data.inputs.test_input
        test_textarea = data.inputs.test_textarea
        test_radio = data.inputs.test_radio

        api_kwargs = {
            'biz_biz_id': biz_cc_id,
            'executor': executor,
            'test_input': test_input,
            'test_textarea': test_textarea,
            'test_radio': test_radio,
        }

        api_result = client.test_api.test1(api_kwargs)
        logger.info('test_api result: {result}, api_kwargs: {kwargs}'.format(result=api_result, kwargs=api_kwargs))
        if api_result['result']:
            data.set_outputs('data1', api_result['data']['data1'])
            return True
        else:
            data.set_outputs('ex_data', api_result['message'])
            return False

    def outputs_format(self):
        return [
            self.OutputItem(name=_(u'ResultData1'), key='data1', type='string')
        ]


class TestCustomComponent(Component):
    name = _(u"CustomPluginTest")
    code = 'test_custom'
    bound_service = TestCustomService
    form = '%scustom_plugins/plugin.js' % settings.STATIC_URL
    version = '1.1.0'

```

The meaning of each attribute and class is:

- `__group_name__`: the group to which the standard plugin belongs (it usually corresponds to the system abbreviation corresponding to the API, such as CMDB).
- `class TestCustomService(Service)`: standard plugin background execution logic
- `class TestCustomComponent(Component)`: standard plugin definition, frontend and backend service binding.

TestCustomService class explanation:

- `__need_schedule__`: whether it is an asynchronous standard plugin (including asynchronous polling and asynchronous callback). It is set to False by default.
- `interval`: the polling policy of asynchronous standard plugin
- `def execute_pre_process`: pre-processing before standard plugin execution. It can pre-process and validate plugin input data and return a True/False result. If the result is False, execute function will not be called.
- `def execute`: Standard plugin execution logic, including frontend parameter acquisition, API parameter assembly, result analysis and result output.
- `def schedule`: the polling or callback logic of asynchronous standard plugin. This method does not need to be defined when using synchronous standard plugin.
- `def outputs_format`: output parameters definition.
- `def inputs_format`: input parameters definition.

execute_pre_process function explanation:

- It can be any python code. It validates and pre-processes the plugin data and returns a pre-process result. The function is not necessary, and it returns True by default.
- data is the standard plugin parameter data input and output object. The input parameter corresponds to the form in the frontend. A parameter can be acquired by using `data.inputs.xxx` or `data.get_one_of_inputs('xxx')`
; After execution, `data.set_outputs` can be used to write output parameter. Exceptions should be assigned to `ex_data`.
- `parent_data` is the public parameter of task. It includes executor (executor), operator (operator), biz_cc_id (business ID), etc. Refer to
`gcloud/taskflow3/utils.py` for details.
- `False` means the pre-process or validation failed. The failed execution result and exception will be returned, and `execute` and `schedule` function will not be executed;
`True` means the pre-process or validation is successful and `execute` function will be executed normally.

execute function explanation:

- It can be any python code, if Blueking API gateway interface needs to be called. It consists of parameter assembly, API call, and result parsing.
- data is the standard plugin parameter data input and output object. The input parameter corresponds to the form in the frontend. A parameter can be acquired by using `data.inputs.xxx` or `data.get_one_of_inputs('xxx')`
; After execution, `data.set_outputs` can be used to write output parameter. Exceptions should be assigned to `ex_data`.
- `parent_data` is the public parameter of task. It includes executor (executor), operator (operator), biz_cc_id (business ID), etc. Refer to
`gcloud/taskflow3/utils.py` for details.
- `False` means execution failed. When synchronous plugin returns `True`, it means standard plugin execution success. When asynchronous plugin returns `True`, it will go into hibernation and wait for the first asynchronous polling or external
callback, then execute `schedule` function.

outputs_format function explanation:

- Return the list of output parameters.
- Each item in the list format defines a returned field, which is a subset of the output field of `set_outputs` in `execute` function; `key` is the output field identifier, `name` is the output field definition,
`type` is the output field type (`str`, `int` and other `python` data structure).

inputs_format function explanation:
- Return the list of input parameters.
- This method provides an explanation of the input parameter and does not affect code execution.

schedule function explanation:

- The scheduling strategy is controlled by the `interval` attribute of the `TestCustomService` class, such as `pipeline.core.flow.activity.StaticIntervalGenerator`
(seconds between each polling), `SquareIntervalGenerator`(The interval between each polling is the square of the current scheduled times).
- Use `self.finish_schedule` to end polling. `True` indicates that the standard plugin has been executed successfully. `False` indicates execution failed.


TestCustomComponent class explanation:
- `name`: standard plugin name.
- `code`: the unique ID of standard plugin, please keep `code` and `version` globally unique.
- `bound_service`: bind backgound service `TestCustomService`.
- `form`: frontend form file path, please add `settings.STATIC_URL` prefix.
- `version`: plugin version number string. Used for version control of plugins with the same `code`.

#### Plugin version control

Sometimes, we need to update a certain plugin, such as adding new fields to the form, adding new functions to the background logic. For this, we need to modify the logic of the current plugin; If the current user flow and task are using this plugin, modifying the code of the plugin directly may cause the current flow and tasks to become unavailable, so the correct approach should be adding a new version of this plugin.

By configuring the `version` class attribute of Component, we can set plugins with the same `code` to different version. This will ensure that the plugin function update will not affect the user. The user simply needs to update the old plugin when necessary.

**Note: please don't add the `version` field to the plugins without `version` parameter. The system may treat it as a new plugin, and templates and tasks may not work properly.**

> There are no restrictions on how the version field is written. However, it is best to use comprehensible nomenclature.


### 5. Standard plugin frontend development

The frontend logic is written in `plugin.js` file. Configure the standard operation frontend plugin framework to generate frontend form. A sample code is given below.
```js
(function(){
    $.atoms.test_custom = [
        {
            tag_code: "test_input",
            type: "input",
            attrs: {
                name: gettext("Parameter 1"),
                placeholder: gettext("Please enter string"),
                hookable: true,
                validation: [
                    {
                        type: "required"
                    }
                ]
            }
        },
        {
            tag_code: "test_textarea",
            type: "textarea",
            attrs: {
                name: gettext("Parameter 2"),
                placeholder: gettext("separated by line break"),
                hookable: true,
                validation: [
                    {
                        type: "required"
                    }
                ]
            }
        },
        {
            tag_code: "test_radio",
            type: "radio",
            attrs: {
                name: gettext("Parameter 3"),
                items: [
                    {value: "1", name: gettext("Option 1")},
                    {value: "2", name: gettext("Option 2")},
                    {value: "3", name: gettext("Option 3")}
                ],
                default: "1",
                hookable: true,
                validation: [
                    {
                        type: "required"
                    }
                ]
            }
        }
    ]
})();

```

Standard plugin frontend configuration is registered through $.atoms. The various items are:

- `test_custom`: the code defined in the standard plugin background
- `tag_code`: parameter code. Please keep this one globally unique, the naming convention is "SystemName_ParameterName".
- `type`: frontend form type. The options are: input, textarea, radio, checkbox, select, datetime, datatable, upload, combine,etc.
- `attrs`: Attribute settings for the corresponding type, such as name, validation, etc.

In addition, form items from another standard plugin can be inherited by the standard plugin frontend configuration. The following attributes need to be defined:

- `extend`: Inherit the form items from another standard plugin. Format: `Base.TagA.TagB...`, `Base` is the name of other plugins. `Tag` is the value of `tag_code` of plugin form items. If only the `Base` value is define, all form items in that standard plugin will be inherited.
- `config`: overwrites the inherited standard plugin form item configuration. It is not a required attribute. The data type should be identical to the inherited configuration item data type. If the inherited configuration is an object, then config object's tag_code needs to be set to the tag_code value of the inherited object. The attributes of two objects should be added together. When there is a same attribute, the config object attribute value will replace the inherited object attribute value; If the inherited configuration is an array. For example, in a scenario where only `Base` is defined, config needs to be set to array. Form configuration elements in the array will be merged with the inherited configuration. The overwrite rules for configuration items with the same tag_code remains the same.

An example of standard plugin frontend inheritance:

```js
// base.js
(function () {
    $.atoms.base_custom = [
        {
            tag_code: "test_input",
            type: "input",
            attrs: {
                name: gettext("Parameter 1"),
                placeholder: gettext("Please enter string"),
                hookable: true,
                validation: [
                    {
                        type: "required"
                    }
                ]
            }
        }
    ]
})()

// test_custom.js
(function () {
    $.atoms.test_custom = [
        {
            extend: "base.test_input",
            config: {
                tag_code: "test_input",
                type: "textarea"
            }
        },
        {
            tag_code: "test_radio",
            type: "radio",
            attrs: {
                name: gettext("Parameter 3"),
                items: [
                    {value: "1", name: gettext("Option 1")},
                    {value: "2", name: gettext("Option 2")},
                    {value: "3", name: gettext("Option 3")}
                ],
                default: "1",
                hookable: true,
                validation: [
                    {
                        type: "required"
                    }
                ]
            }
        }
    ]
})()

// The test_custom.js after successful inheritance
(function () {
    $.atoms.test_custom = [
        {
            tag_code: "test_input",
            type: "text", // type attribute is overwritten
            attrs: {
                name: gettext("Parameter 1"),
                placeholder: gettext("Please enter string"),
                hookable: true,
                validation: [
                    {
                        type: "required"
                    }
                ]
            }
        }
        {
            tag_code: "test_radio",
            type: "radio",
            attrs: {
                name: gettext("Parameter 3"),
                items: [
                    {value: "1", name: gettext("Option 1")},
                    {value: "2", name: gettext("Option 2")},
                    {value: "3", name: gettext("Option 3")}
                ],
                default: "1",
                hookable: true,
                validation: [
                    {
                        type: "required"
                    }
                ]
            }
        }
    ]
})()

```


For details on field descriptions, please refer to: [Tag Usage and Development](./tag_usage_dev.md).

### 6. Standard plugin remote loading

Standard plugins outside the system can be loaded in SOPS. However, these plugins have to meet the following requirements (If your plugin does not need to be loaded remotely, you can skip this chapter):

- It needs to declare the third-party python component library that does not exist in the system
- The embedding method used by the plugin form

#### Component library dependency declaration

If your plugin requires a third-party python plugin that does not exist when SOPS is running, you need to
add  `__requirements__` variable in `{CUSTOM PLUGINS NAME}/__init__.py` and declare the name and version number of the component:

```python

# {CUSTOM PLUGINS NAME}/__init__.py

__requirements__ = [
    "flask==x.x.x", # version restriction
    "mako", # no version restriction
]
```

#### Embedded form

Remotely loaded plugins currently do not support reading plugin frontend forms from static files, so the form should be added to the background definition of the plugin by embedding:

- Add `embedded_form` attribute to  Component class and set the value to `True`
- Add `form` attribute to the Component class and set its value to form definition

The following example shows how to declare plugin embedded form defined in section 4 and 5:

```python
class TestCustomComponent(Component):
    name = _(u"CustomPluginTest")
    code = 'test_custom'
    bound_service = TestCustomService
    embedded_form = True  # Embedded form declaration
    # Define form
    form = """ 
    (function(){
        $.atoms.test_custom = [
            {
                tag_code: "test_input",
                type: "input",
                attrs: {
                    name: gettext("Parameter 1"),
                    placeholder: gettext("Please enter string"),
                    hookable: true,
                    validation: [
                        {
                            type: "required"
                        }
                    ]
                }
            },
            {
                tag_code: "test_textarea",
                type: "textarea",
                attrs: {
                    name: gettext("Parameter 2"),
                    placeholder: gettext("separated by line break"),
                    hookable: true,
                    validation: [
                        {
                            type: "required"
                        }
                    ]
                }
            },
            {
                tag_code: "test_radio",
                type: "radio",
                attrs: {
                    name: gettext("Parameter 3"),
                    items: [
                        {value: "1", name: gettext("Option 1")},
                        {value: "2", name: gettext("Option 2")},
                        {value: "3", name: gettext("Option 3")}
                    ],
                    default: "1",
                    hookable: true,
                    validation: [
                        {
                            type: "required"
                        }
                    ]
                }
            }
        ]
    })();
    """
```

### 7. Standard plugin unit testing

After we complete developing a custom component, we need to test that the component works as intended. The easiest way to do this is to create a workflow that contains the node and run the workflow to
see if the node behaves and generates output as intended. However, this is a very time-consuming and one-time test. We have to run the same test again if the node is modified.

To solve this problem, a component unit testing framework is provided within the framework. The testing framework will simulate an environment for the component to run in and use test cases written by the developer to check
whether the behavior of the component meets expectations. Thanks to the component unit testing framework, we can spend less time on testing. It also enables us to check whether changes will affect the functionality of the component.

Unit test for standard plugin requires a test file to be created in the same subdirectory path as the plugin definition file in `{CUSTOM PLUGINS NAME}/tests`. For example,
for plugins in `{CUSTOM PLUGINS NAME}/components/collections/plugins.py`,
you should create the corresponding testing files for each plugin and create unit testing under `{CUSTOM PLUGINS NAME}/tests/components/collections/plugins_test`.
Additionally, the test file name should be `test_{code}.py`, whereas `{code}` is the unique ID of the plugin.

For instructions on writing unit tests, please refer to: [Writing standard plugin unit test](../../pipeline/docs/user_guide_component_unit_test.md).


### 8. Standard plugin function test

After a plugin is developed, you should execute `python manage.py collectstatic –noinput` at root directory to collect static resources.

Then create a workflow template and add standard plugin node. Select new standard plugin as standard plugin type and make sure that the displayed input parameter is identical to frontend configuration and the output parameter is identical to backend outputs_format.
The execution result is system default. The `True`/`False` value indicates whether the node has been executed successfully.

Then use the created workflow to create a task, fill in the parameters and execute. After execution, check whether the result meets expectation. Use logs to evaluate the result more accurately.


## Standard plugin development specification

- The naming convention for groups is "System name(System Abbreviation)". Example: Job Platform(JOB).
- Use underscore in standard plugin code name: "SystemName_InterfaceName". Example: job_execute_task.
- Use camel case for backend class names: "StandardPluginCode+ClassName". Example: JobExecuteTaskService.
- The file directory name of frontend JS should be identical to system abbreviation. The file name of JS should be identical to standard plugin code.
- The naming convention for tag_code parameter is "SystemName_ParameterName". This is to ensure that the name is globally unique; The length should not exceed 20 characters.
- Please apply translation function to Chinese characters in backend and frontend for future internalization and localization.

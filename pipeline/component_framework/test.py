# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import logging
import importlib

from abc import abstractproperty

from pipeline.core.data.base import DataObject

logger = logging.getLogger(__name__)


class ComponentTestMixin(object):

    @abstractproperty
    def component_cls(self):
        raise NotImplementedError()

    @abstractproperty
    def cases(self):
        raise NotImplementedError()

    @property
    def _component_cls_name(self):
        return self.component_cls.__name__

    def _format_failure_message(self, no, name, msg):
        return '[{component_cls} case {no}] - [{name}] fail: {msg}'.format(
            component_cls=self._component_cls_name,
            no=no + 1,
            name=name,
            msg=msg
        )

    def _do_case_assert(self,
                        service,
                        method,
                        assertion,
                        no,
                        name,
                        args=None,
                        kwargs=None):

        do_continue = False
        args = args or [service]
        kwargs = kwargs or {}

        data = kwargs.get('data') or args[0]

        if assertion.exc:
            # raise assertion

            try:
                getattr(service, method)(*args, **kwargs)
            except Exception as e:
                assert e.__class__ == assertion.exc, self._format_failure_message(
                    no=no,
                    name=name,
                    msg='{method} raise assertion failed,\nexcept: {e}\nactual: {a}'.format(
                        method=method,
                        e=assertion.exc,
                        a=e.__class__
                    ))
                do_continue = True
            else:
                self.assertTrue(False, msg=self._format_failure_message(
                    no=no,
                    name=name,
                    msg='{method} raise assertion failed, {method} not raise any exception'.format(
                        method=method
                    )
                ))

        else:

            result = getattr(service, method)(*args, **kwargs)

            if result is None or result is True:
                self.assertTrue(assertion.success, msg=self._format_failure_message(
                    no=no,
                    name=name,
                    msg='{method} success assertion failed, {method} execute success'.format(
                        method=method
                    )
                ))

                self.assertDictEqual(data.outputs, assertion.outputs, msg=self._format_failure_message(
                    no=no,
                    name=name,
                    msg='{method} outputs assertion failed,\nexcept: {e}\nactual: {a}'.format(
                        method=method,
                        e=data.outputs,
                        a=assertion.outputs
                    )
                ))

            else:
                self.assertFalse(assertion.success, msg=self._format_failure_message(
                    no=no,
                    name=name,
                    msg='{method} success assertion failed, {method} execute failed'.format(
                        method=method
                    )
                ))

                do_continue = True

        return do_continue

    def _do_call_assertion(self, name, no, assertion):
        try:
            assertion.do_assert()
        except AssertionError as e:
            self.assertTrue(False, msg=self._format_failure_message(
                no=no,
                name=name,
                msg='{func} call assert failed: {e}'.format(
                    func=assertion.func,
                    e=e
                )
            ))

    def test_component(self):
        component = self.component_cls({})

        bound_service = component.service()

        for no, case in enumerate(self.cases):
            for patcher in case.patchers:
                patcher.start()

            data = DataObject(inputs=case.inputs)
            parent_data = DataObject(inputs=case.parent_data)

            # execute result check
            do_continue = self._do_case_assert(service=bound_service,
                                               method='execute',
                                               args=(data, parent_data),
                                               assertion=case.execute_assertion,
                                               no=no,
                                               name=case.name)

            for call_assertion in case.execute_call_assertion:
                self._do_call_assertion(name=case.name,
                                        no=no,
                                        assertion=call_assertion)

            if do_continue:
                continue

            if bound_service.need_schedule():

                if bound_service.interval is None:
                    # callback case
                    self._do_case_assert(service=bound_service,
                                         method='schedule',
                                         args=(data, parent_data, case.schedule_assertion.callback_data),
                                         assertion=case.schedule_assertion,
                                         no=no,
                                         name=case.name)

                else:
                    # schedule case
                    assertions = case.schedule_assertion
                    assertions = assertions if isinstance(assertions, list) else [assertions]

                    for assertion in assertions:
                        do_continue = self._do_case_assert(service=bound_service,
                                                           method='schedule',
                                                           args=(data, parent_data),
                                                           assertion=assertion,
                                                           no=no,
                                                           name=case.name)

                        if do_continue:
                            break

                for call_assertion in case.schedule_call_assertion:
                    self._do_call_assertion(name=case.name,
                                            no=no,
                                            assertion=call_assertion)

            for patcher in case.patchers:
                patcher.stop()

        logger.info('{component} paas {num} cases.'.format(
            component=self._component_cls_name,
            num=len(self.cases)
        ))


class ComponentTestCase(object):
    def __init__(self,
                 inputs,
                 parent_data,
                 execute_assertion,
                 schedule_assertion,
                 name='',
                 patchers=None,
                 execute_call_assertion=None,
                 schedule_call_assertion=None):
        self.inputs = inputs
        self.parent_data = parent_data
        self.execute_assertion = execute_assertion
        self.execute_call_assertion = execute_call_assertion or []
        self.schedule_call_assertion = schedule_call_assertion or []
        self.schedule_assertion = schedule_assertion
        self.name = name
        self.patchers = patchers or []


class CallAssertion(object):
    def __init__(self, func, calls, any_order=False):
        self.func = func
        self.calls = calls
        self.any_order = any_order

    def do_assert(self):
        module_and_func = self.func.rsplit('.', 1)
        mod_path = module_and_func[0]
        func_name = module_and_func[1]
        mod = importlib.import_module(mod_path)
        func = getattr(mod, func_name)

        if not self.calls:
            func.assert_not_called()
        else:
            assert func.call_count == len(self.calls), "Expected 'mock' have been called {expect} times. " \
                                                       "Called {actual} times".format(expect=len(self.calls),
                                                                                      actual=func.call_count)
            func.assert_has_calls(calls=self.calls, any_order=self.any_order)

        func.reset_mock()


class Assertion(object):
    def __init__(self, success, outputs, exc=None):
        self.success = success
        self.outputs = outputs
        self.exc = exc


class ExecuteAssertion(Assertion):
    pass


class ScheduleAssertion(Assertion):
    def __init__(self, callback_data, *args, **kwargs):
        self.callback_data = callback_data
        super(ScheduleAssertion, self).__init__(*args, **kwargs)

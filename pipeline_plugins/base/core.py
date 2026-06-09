# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import copy
import logging
import re

import json

from bamboo_engine.template import Template
from django.conf import settings
from pipeline.core.flow.activity import Service
from pipeline.eri.runtime import BambooDjangoRuntime
from pipeline.utils.collections import FancyDict

from gcloud.utils import crypto

from gcloud.core.trace import (
    PLUGIN_SCHEDULE_COUNT_KEY,
    PLUGIN_SPAN_ENDED_KEY,
    PLUGIN_SPAN_ID_KEY,
    clean_plugin_span_outputs,
    end_plugin_span,
    plugin_method_span,
    start_plugin_span,
)

logger = logging.getLogger("root")

PASSWORD_MASK_VALUE = "******"


def _camel_to_snake(name):
    """
    将驼峰命名转换为下划线命名
    例如: JobExecuteTaskService -> job_execute_task

    :param name: 驼峰命名的字符串
    :return: 下划线命名的字符串
    """
    # 移除末尾的 "Service"
    name = re.sub(r"Service$", "", name)
    # 在大写字母前插入下划线（除了第一个字符）
    name = re.sub(r"(?<!^)(?=[A-Z])", "_", name)
    # 转换为小写
    return name.lower()


class BasePluginService(Service):
    """
    插件基类，提供统一的 Span 追踪功能
    所有插件应该继承此类而不是直接继承 Service
    """

    # 是否启用插件 Span 追踪，子类可以覆盖
    enable_plugin_span = True

    def _get_trace_context(self, data, parent_data):
        """
        获取 trace context，包括从 parent_data 中获取的 trace_id 和 parent_span_id，
        以及从 data.outputs 中获取的 plugin_span_id

        :param data: 插件数据对象
        :param parent_data: 父级数据对象
        :return: 包含 trace_id、parent_span_id 和 plugin_span_id 的字典
        """
        return {
            "trace_id": parent_data.get_one_of_inputs("_trace_id"),
            "parent_span_id": parent_data.get_one_of_inputs("_parent_span_id"),
            "plugin_span_id": data.get_one_of_outputs(PLUGIN_SPAN_ID_KEY),
        }

    def _get_span_name(self):
        """
        获取 Span 名称，子类可以覆盖此方法来自定义名称

        :return: Span 名称
        """
        # 将类名从驼峰命名转换为下划线命名
        # 例如: JobExecuteTaskService -> job_execute_task
        plugin_name = _camel_to_snake(self.__class__.__name__)
        platform_code = getattr(settings, "APP_CODE", "bk_sops")
        return f"{platform_code}.plugin.{plugin_name}"

    def _get_span_attributes(self, data, parent_data):
        """
        获取 Span 属性，子类可以覆盖此方法来添加自定义属性

        :param data: 插件数据对象
        :param parent_data: 父级数据对象
        :return: 属性字典
        """
        attributes = {
            "project_id": parent_data.get_one_of_inputs("project_id"),
            "bk_biz_id": parent_data.get_one_of_inputs("bk_biz_id"),
            "task_id": parent_data.get_one_of_inputs("task_id"),
            "operator": parent_data.get_one_of_inputs("operator"),
            "executor": parent_data.get_one_of_inputs("executor"),
            "node_id": self.id,
            "plugin_type": "builtin",  # 内置插件
        }

        return attributes

    def _get_method_span_attributes(self, data, parent_data):
        """
        获取方法级别 Span 属性

        :param data: 插件数据对象
        :param parent_data: 父级数据对象
        :return: 属性字典
        """
        attributes = self._get_span_attributes(data, parent_data)
        # 添加插件名称，将类名从驼峰命名转换为下划线命名
        plugin_name = _camel_to_snake(self.__class__.__name__)
        attributes["plugin_name"] = plugin_name
        return attributes

    def _get_error_message(self, data):
        """
        获取错误信息

        :param data: 插件数据对象
        :return: 错误信息字符串
        """
        ex_data = data.get_one_of_outputs("ex_data")
        if ex_data:
            return str(ex_data)
        return "Plugin execution failed"

    def _start_plugin_span(self, data, parent_data):
        """
        启动插件执行 Span

        :param data: 插件数据对象
        :param parent_data: 父级数据对象
        """
        if not self.enable_plugin_span or not settings.ENABLE_OTEL_TRACE:
            return

        span_name = self._get_span_name()
        attributes = self._get_span_attributes(data, parent_data)

        trace_id = parent_data.get_one_of_inputs("_trace_id")
        parent_span_id = parent_data.get_one_of_inputs("_parent_span_id")

        start_plugin_span(
            span_name=span_name,
            data=data,
            trace_id=trace_id,
            parent_span_id=parent_span_id,
            **attributes,
        )
        data.set_outputs(PLUGIN_SPAN_ENDED_KEY, False)

    def _end_plugin_span(self, data, success, error_message=None):
        """
        结束插件执行 Span（确保只调用一次），并清理 data.outputs 中的 span 相关内部属性

        :param data: 插件数据对象
        :param success: 是否成功
        :param error_message: 错误信息
        """
        if not self.enable_plugin_span or not settings.ENABLE_OTEL_TRACE:
            return

        if data.get_one_of_outputs(PLUGIN_SPAN_ENDED_KEY, False):
            return  # 幂等保护

        end_plugin_span(data, success=success, error_message=error_message)

        # 清理 data.outputs 中所有 span 相关的内部属性，
        # 避免这些非用户需要的内置属性出现在流程任务的输出中
        clean_plugin_span_outputs(data)

    def _auto_decrypt_password_inputs(self, data, input_password_refs=None, mask_flag=False):
        """
        自动识别并解密 data.inputs 中的密码变量值（包括嵌套结构）。
        返回修改记录列表用于恢复。

        :param data: 插件数据对象
        :param input_password_refs: 密码变量引用字典，用于解密密码变量值(只会在value是str类型才会使用)
        :param mask_flag: 本次是否是掩码处理
        """
        try:
            inputs = data.get_inputs()
        except Exception:
            return

        if not inputs:
            return

        for key, value in list(inputs.items()):
            # 顶层 value 直接是密码结构体
            if isinstance(value, dict) and value.get("type") == "password_value":
                self._try_decrypt_value(value, inputs, key, mask_flag=mask_flag)
            # 容器类型，递归进入查找嵌套密码结构体
            elif isinstance(value, (dict, list)):
                self._decrypt_nested_passwords(value, input_password_refs=input_password_refs, mask_flag=mask_flag)
            elif isinstance(value, str):
                self._try_decrypt_value(value, inputs, key, input_password_refs=input_password_refs,
                                        mask_flag=mask_flag)

    def _try_decrypt_value(self, password_struct, container, key_or_index, input_password_refs=None, mask_flag=False):
        """
        尝试解密一个密码结构体,会根据 password_struct 动态处理

        :param password_struct:
            password_struct:dict,如下结构
                密码结构体 dict，如 {"type": "password_value", "value": "rsa_str:::***"};
            password_struct:str,如下结构
                密码结构体 string，如 xxxx{"type": "password_value", "value": "rsa_str:::***"}xxxx;
        :param container: 包含这个密码结构体的父容器（dict 或 list）
        :param key_or_index: 密码结构体在容器中的 key（dict）或 index（list）
        :param input_password_refs: 密码变量引用字典，用于解密密码变量值(只会在value是str类型才会使用)
        :param mask_flag: 本次是否是掩码处理
        """

        plugin_name = _camel_to_snake(self.__class__.__name__)

        def get_decrypt_value(_password_struct):
            cipher = _password_struct.get("value")
            if not cipher or not isinstance(cipher, str):
                return
            try:
                plain = crypto.decrypt(cipher)
            except Exception:
                logger.warning(
                    "[%s] auto decrypt password input failed",
                    plugin_name,
                )
                return
            return plain

        if isinstance(password_struct, str):
            if not input_password_refs:
                return
            for encrypted_password in input_password_refs.values():
                str_password = json.dumps(encrypted_password).replace('"', "'")

                plain = get_decrypt_value(encrypted_password)
                if plain is None:
                    continue
                replace_value = PASSWORD_MASK_VALUE if mask_flag else plain

                # 使用 str.replace 直接替换加密后的字符串
                if str_password in password_struct:
                    password_struct = password_struct.replace(str_password, replace_value)
            container[key_or_index] = password_struct
        elif isinstance(password_struct, dict):
            plain = get_decrypt_value(password_struct)
            if plain is None:
                return
            # 替换为明文
            container[key_or_index] = PASSWORD_MASK_VALUE if mask_flag else plain

    def _decrypt_nested_passwords(self, obj, input_password_refs=None, mask_flag=False):
        """
        递归遍历 obj（dict 或 list），找到所有密码结构体并解密
        """
        if isinstance(obj, dict):
            for k, v in list(obj.items()):
                if isinstance(v, dict) and v.get("type") == "password_value":
                    # v 本身是密码结构体，解密替换
                    self._try_decrypt_value(v, obj, k, mask_flag=mask_flag)
                elif isinstance(v, (dict, list)):
                    # v 是嵌套容器，递归进入其内部继续查找
                    self._decrypt_nested_passwords(v, input_password_refs=input_password_refs, mask_flag=mask_flag)
                elif isinstance(v, str):
                    self._try_decrypt_value(v, obj, k, input_password_refs=input_password_refs, mask_flag=mask_flag)

        elif isinstance(obj, list):
            for idx, v in enumerate(obj):
                if isinstance(v, dict) and v.get("type") == "password_value":
                    # v 本身是密码结构体，解密替换
                    self._try_decrypt_value(v, obj, idx, mask_flag=mask_flag)
                elif isinstance(v, (dict, list)):
                    # v 是嵌套容器，递归进入其内部继续查找
                    self._decrypt_nested_passwords(v, input_password_refs=input_password_refs, mask_flag=mask_flag)
                elif isinstance(v, str):
                    self._try_decrypt_value(v, obj, idx, input_password_refs=input_password_refs, mask_flag=mask_flag)

    def _sync_new_fields(self, target, source):
        """
        将 source 中新增的字段同步到 target 中。
        只同步 target 中不存在的字段（即插件新增的字段），不更新已有字段。
        支持嵌套的 dict 和 list 结构。

        这个方法的目的是：将插件执行后对 data.inputs 新增的字段同步到 copy_data.inputs 和 copy_data_mask.inputs 中，
        这样在做掩码处理时不会丢失插件对 inputs 新增的字段。

        :param target: 需要被更新的数据（如 copy_data.inputs 或 copy_data_mask.inputs）
        :param source: 源数据（如 data.inputs，包含插件新增的字段）
        """
        if isinstance(source, dict) and isinstance(target, dict):
            for key, source_value in source.items():
                if key not in target:
                    # 如果 target 中不存在该 key，说明是插件新增的字段，直接添加
                    target[key] = copy.deepcopy(source_value)
                elif isinstance(source_value, (dict, list)) and isinstance(target.get(key), (dict, list)):
                    # 如果 target 中存在该 key，且值是容器类型，递归处理
                    self._sync_new_fields(target[key], source_value)
        elif isinstance(source, list) and isinstance(target, list):
            # 对于 list，如果长度相同则按索引递归处理，否则不处理（避免误判）
            if len(source) == len(target):
                for i in range(len(source)):
                    if isinstance(source[i], (dict, list)) and isinstance(target[i], (dict, list)):
                        self._sync_new_fields(target[i], source[i])

    def _deep_update(self, target, source):
        """
        递归地深更新 target，将 source 中的字段更新到 target 中。
        对于嵌套的 dict，会递归更新其中的字段；对于 list，会按索引递归更新。
        对于非容器类型的值，直接替换。

        :param target: 需要被更新的数据（如 data.inputs）
        :param source: 用于更新的数据（如 copy_data_mask.inputs）
        """
        if isinstance(source, dict) and isinstance(target, dict):
            for key, source_value in source.items():
                if key in target and isinstance(target[key], dict) and isinstance(source_value, dict):
                    # 如果 target 中存在该 key，且两边都是 dict，递归更新
                    self._deep_update(target[key], source_value)
                elif key in target and isinstance(target[key], list) and isinstance(source_value, list):
                    # 如果 target 中存在该 key，且两边都是 list，递归更新
                    self._deep_update_list(target[key], source_value)
                else:
                    # 否则直接替换
                    target[key] = copy.deepcopy(source_value)
        elif isinstance(source, list) and isinstance(target, list):
            # 对于 list，如果长度相同则按索引递归处理
            if len(source) == len(target):
                for i in range(len(source)):
                    if isinstance(source[i], dict) and isinstance(target[i], dict):
                        self._deep_update(target[i], source[i])
                    elif isinstance(source[i], list) and isinstance(target[i], list):
                        self._deep_update_list(target[i], source[i])
                    else:
                        target[i] = copy.deepcopy(source[i])

    def _deep_update_list(self, target, source):
        """
        更新 list 类型的数据，处理嵌套结构

        :param target: 目标 list
        :param source: 源 list
        """
        if len(source) == len(target):
            for i in range(len(source)):
                if isinstance(source[i], dict) and isinstance(target[i], dict):
                    self._deep_update(target[i], source[i])
                elif isinstance(source[i], list) and isinstance(target[i], list):
                    self._deep_update_list(target[i], source[i])
                else:
                    target[i] = copy.deepcopy(source[i])

    def execute(self, data, parent_data):
        """
        执行插件，包装原有逻辑并添加 Span 追踪

        :param data: 插件数据对象
        :param parent_data: 父级数据对象
        :return: 执行结果
        """
        self._start_plugin_span(data, parent_data)

        input_password_refs = self._get_raw_password_map()  # 获取密码变量key-对应的加密后的value

        trace_context = self._get_trace_context(data, parent_data)
        method_attrs = self._get_method_span_attributes(data, parent_data)

        # 自动解密 inputs 中引用的全局密码变量，使所有插件都支持输入全局密码变量
        copy_data = copy.deepcopy(data)
        copy_parent_data = copy.deepcopy(parent_data)
        self._auto_decrypt_password_inputs(data, input_password_refs=input_password_refs)
        self._auto_decrypt_password_inputs(parent_data, input_password_refs=input_password_refs)

        # 另外拷贝一份出来做掩码处理，
        copy_data_mask = copy.deepcopy(copy_data)
        copy_parent_data_mask = copy.deepcopy(copy_parent_data)
        self._auto_decrypt_password_inputs(copy_data_mask, input_password_refs=input_password_refs, mask_flag=True)
        self._auto_decrypt_password_inputs(copy_parent_data_mask, input_password_refs=input_password_refs,
                                           mask_flag=True)
        result = False
        try:
            if self.enable_plugin_span and settings.ENABLE_OTEL_TRACE:
                with plugin_method_span(
                        method_name="execute",
                        trace_id=trace_context.get("trace_id"),
                        parent_span_id=trace_context.get("parent_span_id"),
                        plugin_span_id=trace_context.get("plugin_span_id"),
                        **method_attrs,
                ) as span_result:
                    result = self.plugin_execute(data, parent_data)
                    if not result:
                        span_result.set_error(self._get_error_message(data))
            else:
                result = self.plugin_execute(data, parent_data)
        finally:
            # 对data的 input做掩码处理,同时outputs需要继承解密后的数据，方便后续调用
            self._sync_new_fields(copy_data.inputs, data.inputs)
            self._sync_new_fields(copy_data_mask.inputs, data.inputs)
            self._deep_update(data.inputs, copy_data_mask.inputs)
            _mask_meta_system_mask_info = {
                'decrypt_input_data': copy_data.inputs,
            }
            data.inputs._mask_meta_system_mask_info = _mask_meta_system_mask_info

            # 更新parent相关
            self._sync_new_fields(copy_parent_data.inputs, parent_data.inputs)
            self._sync_new_fields(copy_parent_data_mask.inputs, parent_data.inputs)
            self._deep_update(parent_data.inputs, copy_parent_data_mask.inputs)
            _mask_meta_system_parent_mask_info = {
                'decrypt_input_data': copy_parent_data.inputs,
            }
            parent_data.inputs._mask_meta_system_parent_mask_info = _mask_meta_system_parent_mask_info

        if not result:
            self._end_plugin_span(data, success=False, error_message=self._get_error_message(data))
        elif not getattr(self, "__need_schedule__", False):
            # 如果不需要 schedule，说明是同步插件，直接结束 span
            self._end_plugin_span(data, success=True)

        return result

    def schedule(self, data, parent_data, callback_data=None):
        """
        调度插件，包装原有逻辑并添加 Span 追踪

        :param data: 插件数据对象
        :param parent_data: 父级数据对象
        :param callback_data: 回调数据
        :return: 调度结果
        """

        trace_context = self._get_trace_context(data, parent_data)
        method_attrs = self._get_method_span_attributes(data, parent_data)
        input_password_refs = self._get_raw_password_map()  # 获取密码变量key-对应的加密后的value

        # schedule里面每次判断是否有 is_mask ，来恢复 data的输入数据
        _mask_meta_system_mask_info = data.inputs.get("_mask_meta_system_mask_info")
        if _mask_meta_system_mask_info:
            data.inputs = FancyDict(_mask_meta_system_mask_info.get("decrypt_input_data"))

        # 对于data进行解密，同时生成一份掩码版本
        copy_data = copy.deepcopy(data)
        copy_data_mask = copy.deepcopy(data)  # 用于schedule执行完做掩码处理
        self._auto_decrypt_password_inputs(data, input_password_refs=input_password_refs)
        self._auto_decrypt_password_inputs(copy_data_mask, input_password_refs=input_password_refs, mask_flag=True)

        # 对于parent_data可能需要解密
        _mask_meta_system_parent_mask_info = parent_data.inputs.get("_mask_meta_system_parent_mask_info")
        if _mask_meta_system_parent_mask_info:
            parent_data.inputs = FancyDict(_mask_meta_system_parent_mask_info.get("decrypt_input_data"))

        copy_parent_data = copy.deepcopy(parent_data)
        copy_parent_data_mask = copy.deepcopy(parent_data)
        self._auto_decrypt_password_inputs(parent_data, input_password_refs=input_password_refs)
        self._auto_decrypt_password_inputs(copy_parent_data_mask, input_password_refs=input_password_refs,
                                           mask_flag=True)
        result = False
        try:
            if self.enable_plugin_span and settings.ENABLE_OTEL_TRACE:
                schedule_count = data.get_one_of_outputs(PLUGIN_SCHEDULE_COUNT_KEY, 0) + 1
                data.set_outputs(PLUGIN_SCHEDULE_COUNT_KEY, schedule_count)
                method_attrs["schedule_count"] = schedule_count

                with plugin_method_span(
                        method_name="schedule",
                        trace_id=trace_context.get("trace_id"),
                        parent_span_id=trace_context.get("parent_span_id"),
                        plugin_span_id=trace_context.get("plugin_span_id"),
                        **method_attrs,
                ) as span_result:
                    result = self.plugin_schedule(data, parent_data, callback_data)
                    if not result:
                        span_result.set_error(self._get_error_message(data))
            else:
                result = self.plugin_schedule(data, parent_data, callback_data)
        finally:
            # 对data的 input做掩码处理,同时outputs需要继承解密后的数据，方便后续调用
            self._sync_new_fields(copy_data.inputs, data.inputs)
            self._sync_new_fields(copy_data_mask.inputs, data.inputs)
            self._deep_update(data.inputs, copy_data_mask.inputs)

            _mask_meta_system_mask_info = {
                'decrypt_input_data': copy_data.inputs,
            }
            data.inputs._mask_meta_system_mask_info = _mask_meta_system_mask_info

            # 更新parent相关
            self._sync_new_fields(copy_parent_data.inputs, parent_data.inputs)
            self._sync_new_fields(copy_parent_data_mask.inputs, parent_data.inputs)
            self._deep_update(parent_data.inputs, copy_parent_data_mask.inputs)
            _mask_meta_system_parent_mask_info = {
                'decrypt_input_data': copy_parent_data.inputs,
            }
            parent_data.inputs._mask_meta_system_parent_mask_info = _mask_meta_system_parent_mask_info

        if not result:
            self._end_plugin_span(data, success=False, error_message=self._get_error_message(data))
        else:
            # 尝试调用 is_schedule_finished() 方法（如果存在）
            # 如果不存在，则检查 __need_schedule__ 属性
            try:
                if hasattr(self, "is_schedule_finished") and callable(getattr(self, "is_schedule_finished")):
                    if self.is_schedule_finished():
                        self._end_plugin_span(data, success=True)
                elif not getattr(self, "__need_schedule__", False):
                    # 如果不再需要 schedule，说明已完成
                    self._end_plugin_span(data, success=True)
            except Exception:
                # 如果判断失败，不结束 span，让下次 schedule 调用时再判断
                pass

        return result

    def plugin_execute(self, data, parent_data):
        """
        插件执行逻辑，子类应该覆盖此方法而不是 execute

        :param data: 插件数据对象
        :param parent_data: 父级数据对象
        :return: 执行结果
        """
        # 默认实现，子类应该覆盖
        return True

    def plugin_schedule(self, data, parent_data, callback_data=None):
        """
        插件调度逻辑，子类应该覆盖此方法而不是 schedule

        注意：对于需要调度的插件（__need_schedule__ = True），在调度完成时
        必须调用 self.finish_schedule() 来标记调度结束。否则 BasePluginService
        无法感知调度已完成，会导致插件级别的父 Span 无法正确结束和导出。

        :param data: 插件数据对象
        :param parent_data: 父级数据对象
        :param callback_data: 回调数据
        :return: 调度结果
        """
        # 默认实现，子类应该覆盖
        return True

    def _get_raw_password_map(self):
        """
        从 BambooDjangoRuntime 获取当前节点原始输入，解析变量引用，
        从全局上下文中查找加密密码值，返回 {var_name: cipher_text} 映射。
        主要是用于获取所有需要引用密码变量的key和加密后的数据，方便后续做密码映射
        """
        try:
            node_id = self.id
            runtime = BambooDjangoRuntime()

            # 1. 获取当前节点的原始 Data
            raw_data = runtime.get_data(node_id)
            need_render_inputs = raw_data.need_render_inputs()

            # 2. 获取当前节点所属的 top_pipeline_id（根流程 ID）
            #    递归向上找根节点：parent_id 为 None 时说明当前节点就是根流程
            state = runtime.get_state(node_id)
            current_node = node_id
            while state.parent_id:
                current_node = state.parent_id
                state = runtime.get_state(current_node)
            pipeline_id = current_node

            # 3. 获取所有变量引用（如 ${customerMessageContent}）
            refs = set(Template(need_render_inputs).get_reference())
            additional_refs = runtime.get_context_key_references(pipeline_id=pipeline_id, keys=refs)
            inputs_refs = refs.union(additional_refs)

            if not inputs_refs:
                return {}

            # 4. 查询全局上下文中的这些变量
            context_values = runtime.get_context_values(pipeline_id=pipeline_id, keys=inputs_refs)

            # 5. 只保留值是密码结构体的变量
            password_map = {}
            for cv in context_values:
                val = cv.value
                if not isinstance(val, dict):
                    continue
                if val.get("type") != "password_value":
                    continue
                password_map[cv.key] = val

            return password_map
        except Exception:
            plugin_name = _camel_to_snake(self.__class__.__name__)
            logger.warning(
                "[%s] get raw password map failed, fallback to empty map",
                plugin_name,
            )
            return {}

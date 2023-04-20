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
import abc
import datetime
import logging
import re
import typing

from MySQLdb import Connection

from pipeline_plugins.components.collections.sites.open.cc.base import (
    cc_parse_path_text,
)
from pipeline_plugins.components.utils.sites.open.utils import ip_pattern

logger = logging.getLogger("root")


class DBHelper:
    def __init__(self, conn: typing.Optional[Connection], source_env: str, target_env: str):
        self.conn = conn
        self.source_env = source_env
        self.target_env = target_env

    def fetch_resource_id_map(
        self, resource_type: str, source_data: typing.List[typing.Union[int, str]], source_data_type: type
    ) -> typing.Dict[typing.Union[int, str], typing.Union[int, str]]:
        """
        获取资源新老关系映射
        :param resource_type:
        :param source_data:
        :param source_data_type:
        :return:
        """
        source_str_data: typing.List[str] = [f'"{str(source_id)}"' for source_id in source_data]
        with self.conn.cursor() as cursor:
            cursor.execute(
                f"SELECT * FROM bk_job_resource_mapping "
                f'WHERE source_env="{self.source_env}" and target_env="{self.target_env}" '
                f'and resource_type="{resource_type}" and source_data in ({",".join(source_str_data)})'
            )
            columns = [desc[0] for desc in cursor.description]
            job_resource_mapping_infos: typing.List[typing.Dict] = [
                dict(zip(columns, row)) for row in cursor.fetchall()
            ]

        resource_id_map: typing.Dict[typing.Union[int, str], typing.Union[int, str]] = {}
        for job_resource_mapping_info in job_resource_mapping_infos:
            resource_id_map[source_data_type(job_resource_mapping_info["source_data"])] = source_data_type(
                job_resource_mapping_info["target_data"]
            )
        return resource_id_map

    def insert_resource_mapping(
        self,
        table_name: str,
        resource_type: str,
        source_data_target_data_map: typing.Dict[typing.Union[str, int], typing.Union[str, int]],
        source_data_type: type,
    ):
        """
        插入新的映射关系
        :param table_name:
        :param resource_type:
        :param source_data_target_data_map:
        :param source_data_type:
        :return:
        """
        if not source_data_target_data_map:
            return

        data: typing.List[typing.Tuple] = []

        # 采取先删后增的策略
        source_str_data: typing.List[str] = [f'"{str(source_id)}"' for source_id in source_data_target_data_map.keys()]
        with self.conn.cursor() as cursor:
            cursor.execute(
                f"DELETE FROM {table_name} "
                f'WHERE source_env="{self.source_env}" and target_env="{self.target_env}" '
                f'and resource_type="{resource_type}" and source_data in ({",".join(source_str_data)})'
            )

        for source_data, target_data in source_data_target_data_map.items():
            data.append(
                (
                    resource_type,
                    self.source_env,
                    str(source_data),
                    ("Long", "String")[source_data_type == str],
                    self.target_env,
                    str(target_data),
                    ("Long", "String")[source_data_type == str],
                    "sops-migration-tool",
                    int(datetime.datetime.now().timestamp() * 1000),
                    "sops-migration-tool",
                    int(datetime.datetime.now().timestamp() * 1000),
                    "Auto created by sops-migration-tool",
                )
            )

        with self.conn.cursor() as cursor:
            insert_sql: str = (
                f"INSERT INTO {table_name} " f"VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            )
            cursor.executemany(insert_sql, data)
            self.conn.commit()


class SuiteMeta:
    pipeline_tree: typing.Dict[str, typing.Any]
    offset: int
    old_biz_id__new_biz_info_map: typing.Dict[int, typing.Dict[str, typing.Any]]

    def __init__(
        self,
        pipeline_tree: typing.Dict[str, typing.Any],
        offset: int,
        old_biz_id__new_biz_info_map: typing.Dict[int, typing.Dict[str, typing.Any]],
    ):
        """
        :param offset: 自增 ID 相关资源（除业务 ID）外的环境偏移量
        :param old_biz_id__new_biz_info_map: 老业务 ID - 新业务信息映射关系
        """
        self.pipeline_tree = pipeline_tree
        self.offset = offset
        self.old_biz_id__new_biz_info_map = old_biz_id__new_biz_info_map


class Suite(abc.ABC):
    TYPE: str = ""
    CODE: str = ""

    suite_meta: SuiteMeta

    def __init__(self, suite_meta: SuiteMeta, db_helper: DBHelper):
        self.suite_meta = suite_meta
        self.db_helper = db_helper

    @abc.abstractmethod
    def do(self, node_id: str, component: typing.Dict[str, typing.Any]):
        raise NotImplementedError


class CmdbSuite(Suite, abc.ABC):
    def __init__(self, suite_meta: SuiteMeta, db_helper: DBHelper):
        super().__init__(suite_meta, db_helper)

        self.biz_old_name__new_name_map: typing.Dict[str, str] = {
            new_biz_info["bk_old_biz_name"]: new_biz_info["bk_new_biz_name"]
            for new_biz_info in self.suite_meta.old_biz_id__new_biz_info_map.values()
        }

    def to_new_topo_select(self, old_topo_select: str) -> str:
        """
        将拓扑节点选择目标替换为新的目标
        :param old_topo_select:
        :return:
        """

        # handle {bk_inst_id}_{ip}
        try:
            ip_or_bk_inst_id = old_topo_select.split("_")[-1]
        except Exception:
            return old_topo_select

        if ip_pattern.match(ip_or_bk_inst_id):
            bk_inst_id, ip = old_topo_select.rsplit("_", 1)
            bk_inst_id = int(bk_inst_id)
            return f"{bk_inst_id + self.suite_meta.offset}_{ip}"

        try:
            # handle {bk_obj_id}_{bk_inst_id}
            bk_obj_id, bk_inst_id = old_topo_select.rsplit("_", 1)
            bk_inst_id = int(bk_inst_id)
        except Exception:
            return old_topo_select

        if bk_obj_id == "biz":
            # 业务和其他实例的偏移不同，需要单独处理
            bk_new_inst_id: int = self.suite_meta.old_biz_id__new_biz_info_map.get(
                bk_inst_id, {"bk_new_biz_id": bk_inst_id}
            )["bk_new_biz_id"]
            return f"{bk_obj_id}_{bk_new_inst_id}"
        else:
            return f"{bk_obj_id}_{bk_inst_id + self.suite_meta.offset}"

    def to_new_cloud_id(self, old_cloud_id: int) -> int:
        """
        获得迁移后的云区域 ID
        规则：除直连区域（0）外，其他云区域 ID 按规定量偏移
        :param old_cloud_id:
        :return:
        """

        if old_cloud_id == 0:
            return old_cloud_id
        return old_cloud_id + self.suite_meta.offset

    def to_new_ip_list_str_or_raise(self, old_ip_list_str: str) -> str:
        # 匹配出所有格式为 云区域:IP 的输入
        local_ip_pattern = re.compile(r"(\d+:)?((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)(?!\d)")

        cloud_ip_list: typing.List[typing.List] = [
            match.group().split(":") for match in local_ip_pattern.finditer(old_ip_list_str)
        ]

        plat_ip_list: typing.List[str] = []
        without_plat_ip_list: typing.List[str] = []
        for cloud_ip in cloud_ip_list:
            if len(cloud_ip) == 1:
                without_plat_ip_list.append(cloud_ip[0])
            else:
                _cloud, _ip = cloud_ip
                plat_ip_list.append(f"{self.to_new_cloud_id(int(_cloud))}:{_ip}")

        # 最小处理原则，如果填写的 IP 不包含云区域，则不做处理，尽可能不修改用户数据
        if not plat_ip_list:
            return old_ip_list_str

        # 没有匹配到任何 IP，跳过
        if not (plat_ip_list or without_plat_ip_list):
            return old_ip_list_str

        # 使用换行符重新整合处理后的数据
        return "\n".join(without_plat_ip_list + plat_ip_list)

    def get_attr_data_or_raise(self, schema_attr_data: typing.Dict[str, typing.Any]) -> typing.Dict[str, typing.Any]:
        """
        获取表单值的实际引用处
        :param schema_attr_data:
        :return:
        """

        if not schema_attr_data["value"]:
            raise ValueError

        if isinstance(schema_attr_data["value"], str):
            # 尝试找出引用的常量
            attr_data_from_constants: typing.Optional[typing.Dict[str, typing.Any]] = self.suite_meta.pipeline_tree.get(
                "constants", {}
            ).get(schema_attr_data["value"])

            if attr_data_from_constants:
                # 如果变量已被处理，本轮直接跳过
                if attr_data_from_constants.get("resource_replaced"):
                    raise ValueError
                # 标记已处理节点，此处认为取出则一定会被处理，避免变量复用场景被多次处理
                attr_data_from_constants["resource_replaced"] = True
                return attr_data_from_constants
        else:
            attr_data_from_constants = None

        # 如果常量存在，将作为替换目标，否则认为值存在于 schema_attr_data
        attr_data: typing.Dict[str, typing.Any] = attr_data_from_constants or schema_attr_data

        if not attr_data["value"]:
            raise ValueError

        return attr_data

    def to_new_cmdb_id_form(self, component: typing.Dict[str, typing.Any], key: str, source_key: str):
        """
        CMDB 自增 ID 替换
        :param component:
        :param key:
        :param source_key:
        :return:
        """
        if key not in component["data"]:
            return

        try:
            attr_data: typing.Dict[str, typing.Any] = self.get_attr_data_or_raise(component["data"][key])
        except Exception:
            return

        if not isinstance(attr_data["value"], list):
            return

        for item in attr_data["value"]:
            try:
                if isinstance(item[source_key], str):
                    if source_key in ["bk_cloud_id", "nodeman_bk_cloud_id"]:
                        item[source_key] = str(self.to_new_cloud_id(int(item[source_key])))
                    else:
                        item[source_key] = str(int(item[source_key]) + self.suite_meta.offset)
                else:
                    if source_key in ["bk_cloud_id", "nodeman_bk_cloud_id"]:
                        item[source_key] = self.to_new_cloud_id(item[source_key])
                    else:
                        item[source_key] = item[source_key] + self.suite_meta.offset
            except Exception:
                pass

    def process_ip_list_str(self, node_id: str, schema_attr_data: typing.Dict[str, typing.Any]):
        """
        处理 IP 列表字符串，将其中可能存在的云区域 ID 按规则偏移
        :param node_id:
        :param schema_attr_data:
        :return:
        """

        try:
            attr_data: typing.Dict[str, typing.Any] = self.get_attr_data_or_raise(schema_attr_data)
        except ValueError:
            return

        # 类型不符合预期时不做处理
        if not isinstance(attr_data["value"], str):
            return

        try:
            attr_data["value"] = self.to_new_ip_list_str_or_raise(attr_data["value"])
        except ValueError:
            pass

    def process_cc_id(self, node_id: str, schema_attr_data: typing.Dict[str, typing.Any]):
        """
        处理业务 ID
        :param node_id:
        :param schema_attr_data:
        :return:
        """
        try:
            attr_data: typing.Dict[str, typing.Any] = self.get_attr_data_or_raise(schema_attr_data)
        except ValueError:
            return

        # 类型不符合预期时不做处理
        if not isinstance(attr_data["value"], int):
            return

        try:
            new_biz_info: typing.Dict[str, typing.Any] = self.suite_meta.old_biz_id__new_biz_info_map[
                attr_data["value"]
            ]
        except KeyError:
            return

        schema_attr_data["value"] = new_biz_info["bk_new_biz_id"]

    def process_topo_select_text(self, node_id: str, schema_attr_data: typing.Dict[str, typing.Any]):
        """
        处理拓扑文本路径
        :param node_id:
        :param schema_attr_data:
        :return:
        """
        try:
            attr_data: typing.Dict[str, typing.Any] = self.get_attr_data_or_raise(schema_attr_data)
        except ValueError:
            return

        # 类型不符合预期时不做处理
        if not isinstance(attr_data["value"], str):
            return

        path_list = cc_parse_path_text(attr_data["value"])

        new_path_str_list: typing.List[str] = []
        for path in path_list:
            try:
                if path[0] in self.biz_old_name__new_name_map:
                    path[0] = self.biz_old_name__new_name_map[path[0]]
                    new_path_str_list.append(" > ".join(path))
            except IndexError:
                pass

        attr_data["value"] = "\n".join(new_path_str_list)

    def process_topo_select(self, node_id: str, schema_attr_data: typing.Dict[str, typing.Any]):
        """
        处理拓扑节点选择
        :param node_id:
        :param schema_attr_data:
        :return:
        """

        try:
            attr_data: typing.Dict[str, typing.Any] = self.get_attr_data_or_raise(schema_attr_data)
        except ValueError:
            return

        # 类型不符合预期时不做处理
        if not isinstance(attr_data["value"], list):
            return

        new_topo_select_list: typing.List[str] = []
        for topo_select in attr_data["value"]:
            new_topo_select_list.append(self.to_new_topo_select(topo_select))

        attr_data["value"] = new_topo_select_list


class JobSuite(CmdbSuite, abc.ABC):
    def to_new_ip_form(self, component: typing.Dict[str, typing.Any], key: str, ip_key: str):
        """
        IP 表单替换
        :param component:
        :param key:
        :param ip_key:
        :return:
        """
        if key not in component["data"]:
            return

        try:
            attr_data: typing.Dict[str, typing.Any] = self.get_attr_data_or_raise(component["data"][key])
        except Exception:
            return

        if not isinstance(attr_data["value"], list):
            return

        for item in attr_data["value"]:
            try:
                item[ip_key] = self.to_new_ip_list_str_or_raise(item[ip_key])
            except Exception:
                pass

    def to_new_job_id(
        self, component: typing.Dict[str, typing.Any], key: str, resource_type: str, source_data_type: type
    ):
        try:
            attr_data: typing.Dict[str, typing.Any] = self.get_attr_data_or_raise(component["data"][key])

            if isinstance(attr_data["value"], int):
                resource_id_map: typing.Dict[int, int] = self.db_helper.fetch_resource_id_map(
                    resource_type=resource_type, source_data=[attr_data["value"]], source_data_type=source_data_type
                )
                attr_data["value"] = resource_id_map.get(attr_data["value"], attr_data["value"])

        except Exception:
            pass

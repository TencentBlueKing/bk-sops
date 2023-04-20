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
specific lan
"""

import csv
import json
import logging
import typing
import zlib
from collections import defaultdict

from MySQLdb import Connection
from pipeline.models import PipelineTemplate

from gcloud.constants import COMMON
from pipeline_plugins.resource_replacement import base, suites
from pipeline_web.constants import PWE
from pipeline_web.wrapper import PipelineTemplateWebWrapper

logger = logging.getLogger("root")


def blob_data_to_string(blob_string: str) -> str:
    """
    将数据库中 16 进制格式字符串转为原始数据
    :param blob_string: 0x78....
    :return: 解压后的数据
    """
    data = bytes.fromhex(blob_string[2:])
    return zlib.decompress(data).decode("utf-8")


def get_old_biz_id__new_biz_info_map(
    mysql_config: typing.Dict[str, typing.Any], source_env: str
) -> typing.Dict[int, typing.Dict]:
    """
    获取指定环境老业务 ID - 新业务信息映射关系
    :param mysql_config:
    :param source_env: 导出环境代号
    :return:
    """
    with Connection(**mysql_config) as conn:
        with conn.cursor() as cursor:
            cursor.execute(f'SELECT * FROM cc_EnvBizMap WHERE bk_env="{source_env}"')
            columns = [desc[0] for desc in cursor.description]
            cc_env_biz_infos = [dict(zip(columns, row)) for row in cursor.fetchall()]
    return {cc_env_biz_info["bk_old_biz_id"]: cc_env_biz_info for cc_env_biz_info in cc_env_biz_infos}


def get_cc_offset(mysql_config: typing.Dict[str, typing.Any], source_env: str) -> int:
    """
    获取指定环境的 CC 资源自增 ID 偏移量
    :param mysql_config:
    :param source_env: 导出环境代号
    :return:
    """
    with Connection(**mysql_config) as conn:
        with conn.cursor() as cursor:
            cursor.execute(f'SELECT * FROM cc_EnvIDOffset WHERE env="{source_env}"')
            columns = [desc[0] for desc in cursor.description]
            cc_env_offset_infos = [dict(zip(columns, row)) for row in cursor.fetchall()]

    return cc_env_offset_infos[0]["offset"]


def reuse_imported_common_template(
    common_template_id_map: typing.Dict[str, typing.Any], template_data: typing.Dict[str, typing.Any]
):
    """
    复用已导入的公共流程
    :param common_template_id_map: 公共流程导入新应用环境后的 ID 映射关系
    :param template_data: 流程导出数据
    :return:
    """
    scheme_id_old_to_new: typing.Dict[int, int] = common_template_id_map["scheme_id_old_to_new"]
    temp_id_old_to_new: typing.Dict[str, str] = common_template_id_map[PipelineTemplateWebWrapper.ID_MAP_KEY]
    old_tid__template_create_info_map: typing.Dict[str, typing.Dict] = (
        common_template_id_map["template_recreated_info"].get(COMMON) or {}
    )
    new_temp_id__pipeline_obj_map: typing.Dict[str, PipelineTemplate] = {
        obj.template_id: obj for obj in PipelineTemplate.objects.filter(template_id__in=temp_id_old_to_new.values())
    }

    removed_tid_list: typing.List[str] = []
    removed_pipeline_tid_list: typing.List[str] = []
    old_tid__template_map: typing.Dict[str, typing.Dict[str, typing.Any]] = template_data["template"]
    # 将已导入的公共流程，从待导入的流程中移除
    for old_tid, template_create_info in old_tid__template_create_info_map.items():
        if old_tid not in old_tid__template_map:
            continue
        assert (
            template_create_info["export_data"]["pipeline_template_str_id"]
            == old_tid__template_map[old_tid]["pipeline_template_str_id"]
        )
        removed_tid_list.append(old_tid)
        removed_pipeline_tid_list.append(template_create_info["export_data"]["pipeline_template_str_id"])
        old_tid__template_map.pop(old_tid)

    refs: typing.Dict[str, typing.Dict[str, typing.List[str]]] = template_data["pipeline_template_data"]["refs"]
    old_pipeline_tid__info_map: typing.Dict[str, typing.Dict[str, typing.Any]] = template_data[
        "pipeline_template_data"
    ]["template"]

    for removed_pipeline_tid in removed_pipeline_tid_list:
        # 移除公共流程树
        old_pipeline_tid__info_map.pop(removed_pipeline_tid, None)

        # 其余引用到公共流程的地方替换为新创建的树 ID 及版本
        for ref_pipline_tid, act_ids in refs.pop(removed_pipeline_tid, {}).items():
            if ref_pipline_tid not in old_pipeline_tid__info_map:
                continue
            # 移除流程间的相互引用无需处理
            for act_id in act_ids:
                act = old_pipeline_tid__info_map[ref_pipline_tid]["tree"][PWE.activities][act_id]
                if act.get("scheme_id_list"):
                    act["scheme_id_list"] = [
                        scheme_id_old_to_new.get(old_scheme_id, old_scheme_id)
                        for old_scheme_id in act["scheme_id_list"]
                    ]

                act["template_id"] = temp_id_old_to_new[removed_pipeline_tid]
                act["version"] = new_temp_id__pipeline_obj_map[temp_id_old_to_new[removed_pipeline_tid]].version


def add_app_makers(original_project_id: int, template_data: typing.Dict[str, typing.Any], app_maker_csv_filepath: str):
    """
    向已导出的数据中，注入轻应用数据
    :param original_project_id: 原项目 ID
    :param template_data: 导出数据
    :param app_maker_csv_filepath: 轻应用导出数据文件
    :return:
    """
    template_data["app_makers"] = []
    task_template_ids: typing.Set[str] = set(template_data["template"].keys())

    with open(app_maker_csv_filepath) as csvfile:
        # 创建 CSV 文件的读取器
        app_maker_infos_reader = csv.DictReader(csvfile)

        # 遍历每一行数据
        for app_maker_info in app_maker_infos_reader:
            app_maker_info: typing.Dict[str, typing.Any] = app_maker_info
            # 已删除数据 / 不在本项目下的不导入
            if any(
                [
                    not app_maker_info["id"],
                    # csv 读到的文件都是字符串，需要转为实际类型
                    int(app_maker_info["is_deleted"]) == 1,
                    int(app_maker_info["project_id"]) != original_project_id,
                ]
            ):
                continue

            # 不属于导入流程模板的不导入
            if app_maker_info["task_template_id"] not in task_template_ids:
                continue

            template_data["app_makers"].append(
                {
                    "id": int(app_maker_info["id"]),
                    "name": app_maker_info["name"],
                    "desc": app_maker_info["desc"],
                    "username": app_maker_info["creator"],
                    "project_id": original_project_id,
                    "template_id": int(app_maker_info["task_template_id"]),
                    "template_scheme_id": int(app_maker_info["template_scheme_id"])
                    if app_maker_info["template_scheme_id"]
                    else None,
                }
            )


def add_template_schemes(template_data: typing.Dict[str, typing.Any], pipeline_template_scheme_csv_filepath: str):
    """
    向已导出的数据中添加执行方案
    :param template_data: 导出数据
    :param pipeline_template_scheme_csv_filepath: 执行方案导出的数据文件
    :return:
    """
    recorded_ids: typing.Set[int] = set()
    id__pipeline_template_info_map: typing.Dict[int, typing.Dict[str, typing.Any]] = {
        pipeline_template_info["id"]: pipeline_template_info
        for pipeline_template_info in template_data["pipeline_template_data"]["template"].values()
    }
    pipeline_template_db_ids: typing.Set[int] = set(id__pipeline_template_info_map.keys())

    with open(pipeline_template_scheme_csv_filepath) as csvfile:
        # 创建 CSV 文件的读取器
        template_scheme_info_reader = csv.DictReader(csvfile)

        # 遍历每一行数据
        for template_scheme_info in template_scheme_info_reader:
            template_scheme_info: typing.Dict[str, typing.Any] = template_scheme_info
            # 没有 ID 或没有绑定模板的情况下直接跳过
            if not template_scheme_info["id"] or not template_scheme_info["template_id"]:
                continue

            # 过滤掉不属于导出流程的执行方案
            pipeline_template_db_id = int(template_scheme_info["template_id"])
            if pipeline_template_db_id not in pipeline_template_db_ids:
                continue

            recorded_ids.add(pipeline_template_db_id)

            pipeline_template_info: typing.Dict[str, typing.Any] = id__pipeline_template_info_map[
                pipeline_template_db_id
            ]
            # 在导出流程中，初始化执行方案列表
            if "schemes" not in pipeline_template_info:
                pipeline_template_info["schemes"] = []

            pipeline_template_info["schemes"].append(
                {
                    "id": int(template_scheme_info["id"]),
                    "name": template_scheme_info["name"],
                    "unique_id": template_scheme_info["unique_id"],
                    "template_id": pipeline_template_db_id,
                    # 解压 DB 二进制数据
                    "data": json.loads(blob_data_to_string(template_scheme_info["data"])),
                }
            )

        logging.info(f"[add_template_schemes] pipeline template with schemes count -> {len(recorded_ids)}")

        # 按执行方案自增 ID 对数据进行去重
        for pipeline_template_db_id in recorded_ids:
            pipeline_template_info = id__pipeline_template_info_map[pipeline_template_db_id]
            schemes = list({scheme["id"]: scheme for scheme in pipeline_template_info["schemes"]}.values())
            logging.info(
                f"[add_template_schemes] schemes count -> {len(schemes)} to "
                f"pipeline_template({pipeline_template_db_id})"
            )
            pipeline_template_info["schemes"] = schemes


def inject_pipeline_db_id(template_data: typing.Dict[str, typing.Any], pipeline_template_csv_filepath: str):
    """
    注入 PipelineTemplate 自增 ID 到导出数据
    :param template_data: 导出数据
    :param pipeline_template_csv_filepath: 流程模板的数据文件
    :return:
    """
    pipeline_template_ids = set(template_data["pipeline_template_data"]["template"].keys())

    with open(pipeline_template_csv_filepath) as csvfile:
        # 创建 CSV 文件的读取器
        pipeline_template_infos_reader = csv.DictReader(csvfile)

        # 遍历每一行数据
        for pipeline_template_info in pipeline_template_infos_reader:
            pipeline_template_info: typing.Dict[str, typing.Any] = pipeline_template_info
            if not pipeline_template_info["id"]:
                continue

            # 过滤掉不属于导出流程的数据
            if pipeline_template_info["template_id"] not in pipeline_template_ids:
                continue

            # 根据 template_id 索引到导出数据中的流程数据，并将自增 ID 信息注入
            template_data["pipeline_template_data"]["template"][pipeline_template_info["template_id"]]["id"] = int(
                pipeline_template_info["id"]
            )


def pipeline_resource_replacement(
    pipeline_tree: typing.Dict[str, typing.Any],
    cc_offset: int,
    old_biz_id__new_biz_info_map: typing.Dict[int, typing.Dict[str, typing.Any]],
    db_helper: base.DBHelper,
):
    type__code__suite_cls_map: typing.Dict[str, typing.Dict[str, typing.Type[base.Suite]]] = defaultdict(dict)
    for suite_cls in suites.SUITES:
        type__code__suite_cls_map[suite_cls.TYPE][suite_cls.CODE] = suite_cls

    suite_meta: base.SuiteMeta = base.SuiteMeta(
        pipeline_tree=pipeline_tree, offset=cc_offset, old_biz_id__new_biz_info_map=old_biz_id__new_biz_info_map
    )

    logging.info("[pipeline_resource_replacement] start to replace source in activities")
    for node_id, service_act in pipeline_tree["activities"].items():
        code: typing.Optional[str] = service_act.get("component", {}).get("code")
        if code not in type__code__suite_cls_map["component"]:
            continue
        suite: base.Suite = type__code__suite_cls_map["component"][code](suite_meta, db_helper)
        logging.info(f"[pipeline_resource_replacement] node_id -> {node_id}, suite -> {suite.CODE}")
        try:
            suite.do(node_id, service_act["component"])
        except Exception:
            logging.exception(f"[pipeline_resource_replacement] node_id -> {node_id}, suite -> {suite.CODE} failed")

    logging.info("[pipeline_resource_replacement] start to replace source in constants")
    for var_id, constant in pipeline_tree["constants"].items():
        custom_type: typing.Optional[str] = constant.get("custom_type")
        if custom_type not in type__code__suite_cls_map["var"]:
            continue
        suite: base.Suite = type__code__suite_cls_map["var"][custom_type](suite_meta, db_helper)
        logging.info(f"[pipeline_resource_replacement] node_id -> {var_id}, suite -> {suite.CODE}")
        try:
            suite.do(var_id, constant)
        except Exception:
            pass

    for constant in pipeline_tree["constants"].values():
        constant.pop("resource_replaced", None)


def save_resource_mapping(
    db_helper: base.DBHelper, table_name: str, template_source_type: str, id_map: typing.Dict[str, typing.Any]
):
    """
    保存已导入的资源映射关系
    :param db_helper:
    :param table_name:
    :param template_source_type:
    :param id_map:
    :return:
    """
    tid_old_to_new: typing.Dict[int, int] = {
        int(old_tid): int(template_create_info["id"])
        for old_tid, template_create_info in id_map["template_recreated_info"].get(template_source_type, {}).items()
    }
    db_helper.insert_resource_mapping(
        table_name=table_name,
        resource_type=("template_id", "common_template_id")[template_source_type == COMMON],
        source_data_target_data_map=tid_old_to_new,
        source_data_type=int,
    )

    scheme_id_old_to_new: typing.Dict[int, int] = id_map["scheme_id_old_to_new"]
    db_helper.insert_resource_mapping(
        table_name=table_name,
        resource_type="scheme_id",
        source_data_target_data_map=scheme_id_old_to_new,
        source_data_type=str,
    )

    temp_id_old_to_new: typing.Dict[str, str] = id_map[PipelineTemplateWebWrapper.ID_MAP_KEY]
    db_helper.insert_resource_mapping(
        table_name=table_name,
        resource_type="pipeline_template_id",
        source_data_target_data_map=temp_id_old_to_new,
        source_data_type=str,
    )

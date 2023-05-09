# -*- coding: utf-8 -*-
import json
import logging
import os
import typing

from django.core.management.base import BaseCommand
from django.db import transaction
from MySQLdb import Connection

from gcloud.common_template.models import CommonTemplate
from gcloud.constants import COMMON, PROJECT
from gcloud.core.models import Project
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.template_base.domains import (
    dat_import_helper,
    reference_scene_data_importer,
)
from gcloud.template_base.utils import read_template_data_file
from pipeline_plugins.resource_replacement.base import DBHelper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("root")


@transaction.atomic
def do_import(
    template_source_type: str,
    data_file_path: str,
    export_data_dir: str,
    cc_offset: int,
    old_biz_id__new_biz_info_map: typing.Dict[int, typing.Dict[str, typing.Any]],
    db_helper: DBHelper,
    target_project: Project = None,
    original_project_id: int = None,
    import_app_maker: bool = False,
    import_clocked_task: bool = False,
    reuse_common_template: bool = False,
) -> typing.Dict[str, typing.Any]:
    """
    执行导入操作
    :param template_source_type:
    :param data_file_path:
    :param export_data_dir:
    :param cc_offset:
    :param old_biz_id__new_biz_info_map:
    :param db_helper:
    :param target_project:
    :param original_project_id:
    :param import_app_maker:
    :param import_clocked_task:
    :param reuse_common_template:
    :return:
    """
    template_model_cls: TaskTemplate = (TaskTemplate, CommonTemplate)[template_source_type == COMMON]

    with open(data_file_path, mode="r") as data_file:
        r = read_template_data_file(data_file)
        template_data: typing.Dict[str, typing.Any] = r["data"]["template_data"]

    if reuse_common_template:
        # TODO read from export_data_dir
        common_template_id_map = {}
        dat_import_helper.reuse_imported_common_template(common_template_id_map, template_data)

    # 注入执行方案｜依赖 PipelineTemplate 的自增 ID，先行注入
    logger.info("[import] inject pipeline template db id to export pipeline template info")
    dat_import_helper.inject_pipeline_db_id(
        template_data, os.path.join(export_data_dir, "pipeline_pipelinetemplate.csv")
    )
    # 注入执行方案
    logger.info("[import] add template schemes to export pipeline template info")
    dat_import_helper.add_template_schemes(template_data, os.path.join(export_data_dir, "pipeline_templatescheme.csv"))

    if import_app_maker:
        logger.info("[import] add app markers to export data")
        dat_import_helper.add_app_makers(
            original_project_id, template_data, os.path.join(export_data_dir, "appmaker_appmaker.csv")
        )

    extra_params: typing.Dict[str, typing.Any] = {}
    if template_source_type == PROJECT:
        extra_params.update({"project_id": target_project.id})

    for tid, pipeline_template_dict in template_data["pipeline_template_data"]["template"].items():
        logging.info(
            f"[import] start to pipeline_resource_replacement: tid -> {tid}, name -> {pipeline_template_dict['name']}"
        )
        dat_import_helper.pipeline_resource_replacement(
            pipeline_template_dict["tree"], cc_offset, old_biz_id__new_biz_info_map, db_helper
        )

    logger.info("[import] start to import templates")
    import_result: typing.Dict[str, typing.Any] = template_model_cls.objects.import_templates(
        template_data=template_data, override=False, operator="admin", **extra_params
    )

    if not import_result["result"]:
        raise Exception(f"[import] import templates failed, message: {import_result['message']}")
    else:
        logging.info(f"[import] import templates success, message: {import_result['message']}")

    if import_app_maker:
        app_makers: typing.List[typing.Dict[str, typing.Any]] = template_data.get("app_makers") or []
        logging.info(f"[import] import app makers, count -> {len(app_makers)}")
        import_result["old_id__new_app_maker_info_map"] = reference_scene_data_importer.import_app_makers(
            template_data.get("app_makers") or [], import_result["id_map"]
        )

    if import_clocked_task:
        clocked_tasks: typing.List[typing.Dict[str, typing.Any]] = template_data.get("clocked_task") or []
        logging.info(f"[import] import clocked tasks, count -> {len(clocked_tasks)}")
        import_result["old_id__new_clocked_task_info_map"] = reference_scene_data_importer.import_clocked_tasks(
            target_project.id, clocked_tasks, import_result["id_map"]
        )

    return import_result


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("-t", "--template-source-type", help="Template source type", type=str)
        parser.add_argument("-f", "--data-file-path", help=".dat file path", type=str)
        # 对于老版本的标准运维，app-maker / clocked-task 可以采用 .csv 的方式注入到 .dat 文件，此处预留 .csv / json 目录
        parser.add_argument("-d", "--export-data-dir", help="Export data dir", type=str)
        parser.add_argument("-a", "--app-maker", action="store_true", help="Import app makers")
        parser.add_argument("-c", "--clocked-task", action="store_true", help="Import clocked task")
        # 期望达到的效果：公共流程先导入，获取 ID 映射数据，存在
        # 对于项目流程的导入，将不再把被引的公共流程作为项目流程导入，而是复用已导入的公共流程
        parser.add_argument("-r", "--reuse-common-template", action="store_true", help="Reuse common template")

        # 环境相关
        parser.add_argument("-e", "--source-env", help="Source env", type=str)
        parser.add_argument("-g", "--target-env", help="Target env", type=str)
        parser.add_argument("-b", "--original-biz-id", help="Original biz id", type=int)
        parser.add_argument("-o", "--original-project-id", help="Original project id", type=int)

        # 中转 DB 相关
        parser.add_argument("-H", "--host", help="Migration DB host", type=str)
        parser.add_argument("-P", "--port", help="Migration DB port", type=int)
        parser.add_argument("-u", "--user", help="Migration DB user", type=str)
        parser.add_argument("-p", "--password", help="Migration DB password", type=str)
        parser.add_argument("-D", "--common-migration-database", help="Migration DB database name", type=str)
        parser.add_argument(
            "-n",
            "--self-migration-table-name",
            help="Migration table name of sops",
            type=str,
            default="bk_sops_resource_mapping",
        )

    def handle(self, *args, **options):

        logger.info(f"[import] options: \n{json.dumps(options, indent=2)}")

        template_source_type: str = options["template_source_type"]
        data_file_path: str = options["data_file_path"]
        export_data_dir: str = options["export_data_dir"]

        # source_env & target_env
        source_env: str = options["source_env"]
        target_env: str = options["target_env"]
        original_biz_id: typing.Optional[int] = options.get("original_biz_id")
        original_project_id: typing.Optional[int] = options.get("original_project_id")

        import_app_maker: bool = options.get("app_maker", False)
        import_clocked_task: bool = options.get("clocked_task", False)
        reuse_common_template: bool = options.get("reuse_common_template", False)

        common_migration_database: str = options["common_migration_database"]
        self_migration_table_name: str = options["self_migration_table_name"]
        db_config: typing.Dict[str, typing.Any] = {
            "host": options["host"],
            "port": options["port"],
            "user": options["user"],
            "password": options["password"],
        }

        if template_source_type == PROJECT and not original_project_id:
            raise ValueError(f"Original project id required when source type is {PROJECT}")

        cc_offset: int = dat_import_helper.get_cc_offset(
            {**db_config, "db": common_migration_database}, source_env=source_env
        )

        logging.info(f"[import] source_env -> {source_env}, cc_offset -> {cc_offset}")

        old_biz_id__new_biz_info_map: typing.Dict[
            int, typing.Dict[str, typing.Any]
        ] = dat_import_helper.get_old_biz_id__new_biz_info_map(
            {**db_config, "db": common_migration_database}, source_env=source_env
        )
        db_helper: DBHelper = DBHelper(
            conn=Connection(**{**db_config, "db": common_migration_database}),
            source_env=source_env,
            target_env=target_env,
        )

        target_project: typing.Optional[Project] = None
        if template_source_type == PROJECT:
            target_project: Project = Project.objects.get(
                bk_biz_id=old_biz_id__new_biz_info_map[original_biz_id]["bk_new_biz_id"]
            )
            logging.info(
                f"[import] target_project_id -> {target_project.id}, target_biz_id -> {target_project.bk_biz_id}"
            )

        import_result: typing.Dict[str, typing.Any] = do_import(
            template_source_type,
            data_file_path,
            export_data_dir,
            cc_offset,
            old_biz_id__new_biz_info_map,
            db_helper,
            target_project=target_project,
            original_project_id=original_project_id,
            import_app_maker=import_app_maker,
            import_clocked_task=import_clocked_task and template_source_type == PROJECT,
            reuse_common_template=reuse_common_template,
        )

        dat_import_helper.save_resource_mapping(
            db_helper=db_helper,
            table_name=self_migration_table_name,
            template_source_type=template_source_type,
            id_map=import_result["id_map"],
        )

        db_helper.conn.close()

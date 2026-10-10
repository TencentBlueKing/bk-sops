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
import json
import logging
from collections import defaultdict

from django.apps import apps
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import ugettext_lazy as _
from pipeline.exceptions import SubprocessExpiredError
from pipeline.models import PipelineTemplate, TemplateCurrentVersion, TemplateRelationship

from gcloud import err_code
from gcloud.clocked_task.models import ClockedTask
from gcloud.conf import settings
from gcloud.constants import CLOCKED_TASK_NOT_STARTED, COMMON, PROJECT, TASK_CATEGORY, TEMPLATE_EXPORTER_VERSION
from gcloud.core.utils import convert_readable_username
from gcloud.exceptions import FlowExportError
from gcloud.iam_auth.resource_creator_action.signals import batch_create
from gcloud.template_base.utils import fetch_templates_info, replace_template_id
from gcloud.utils import managermixins
from pipeline_web.core.abstract import NodeAttr
from pipeline_web.core.models import NodeInTemplate
from pipeline_web.parser.clean import PipelineWebTreeCleaner
from pipeline_web.wrapper import PipelineTemplateWebWrapper


logger = logging.getLogger("root")


class BaseTemplateManager(models.Manager, managermixins.ClassificationCountMixin):
    def fetch_values(self, id, *values):
        qs = self.filter(id=id).values(*values)

        if not qs:
            raise self.model.DoesNotExist("{}(id={}) does not exist.".format(self.model.__name__, id))

        return qs.first()

    def creator_for(self, id):
        qs = self.filter(id=id).values("pipeline_template__creator")

        if not qs:
            raise self.model.DoesNotExist("{}(id={}) does not exist.".format(self.model.__name__, id))

        return qs.first()["pipeline_template__creator"]

    def create_pipeline_template(self, **kwargs):
        pipeline_tree = kwargs["pipeline_tree"]
        replace_template_id(self.model, pipeline_tree)
        pipeline_template_data = {
            "name": kwargs["name"],
            "creator": kwargs["creator"],
            "description": kwargs["description"],
        }

        pipeline_web_tree = PipelineWebTreeCleaner(pipeline_tree)
        pipeline_web_tree.clean()

        pipeline_template = PipelineTemplate.objects.create_model(pipeline_tree, **pipeline_template_data)

        # create node in template
        NodeInTemplate.objects.create_nodes_in_template(pipeline_template, pipeline_web_tree.origin_data)
        return pipeline_template

    def export_templates(self, template_id_list, **kwargs):
        template_source_type = PROJECT if self.model.__name__ == "TaskTemplate" else COMMON
        templates = list(self.filter(id__in=template_id_list).select_related("pipeline_template").values())
        pipeline_template_id_list = []
        template = {}
        for tmpl in templates:
            pipeline_template_id_list.append(tmpl["pipeline_template_id"])
            tmpl["pipeline_template_str_id"] = tmpl["pipeline_template_id"]
            template[tmpl["id"]] = tmpl

        try:
            pipeline_temp_data = PipelineTemplateWebWrapper.export_templates(pipeline_template_id_list)
        except SubprocessExpiredError as e:
            raise FlowExportError(str(e))

        # 同一流程模板可能因为引用了多个版本而以不同的导出键存在，这里需要取回其原始模板 ID
        all_template_ids = {template_info["template_id"] for template_info in pipeline_temp_data["template"].values()}
        additional_template_id = all_template_ids - set(pipeline_template_id_list)
        subprocess_temp_list = list(
            self.filter(pipeline_template_id__in=additional_template_id).select_related("pipeline_template").values()
        )

        # 项目流程下导出才会处理项目流程中引用了公共流程的情况
        if template_source_type == PROJECT and len(subprocess_temp_list) < len(additional_template_id):
            common_template_model = apps.get_model("template", "CommonTemplate")
            common_subprocess_temp_list = list(
                common_template_model.objects.filter(pipeline_template_id__in=additional_template_id)
                .select_related("pipeline_template")
                .values()
            )
            subprocess_temp_list += common_subprocess_temp_list

        for sub_temp in subprocess_temp_list:
            sub_temp["pipeline_template_str_id"] = sub_temp["pipeline_template_id"]
            template[sub_temp["id"]] = sub_temp

        result = {
            "template": template,
            "pipeline_template_data": pipeline_temp_data,
            "exporter_version": TEMPLATE_EXPORTER_VERSION,
            "template_source": template_source_type,
        }

        if kwargs.get("export_clocked_task"):
            # 导出计划任务
            clocked_task_cls = apps.get_model("clocked_task", "ClockedTask")
            clocked_tasks = []
            for clocked_task_obj in clocked_task_cls.objects.filter(
                template_source=template_source_type, template_id__in=template_id_list
            ):
                clocked_tasks.append(
                    {
                        "id": clocked_task_obj.id,
                        "project_id": clocked_task_obj.project_id,
                        "template_id": clocked_task_obj.template_id,
                        "template_name": clocked_task_obj.template_name,
                        "template_source": clocked_task_obj.template_source,
                        "task_name": clocked_task_obj.task_name,
                        "task_params": json.loads(clocked_task_obj.task_params),
                        "plan_start_time": clocked_task_obj.plan_start_time.strftime(
                            PipelineTemplateWebWrapper.SERIALIZE_DATE_FORMAT
                        ),
                        "edit_time": clocked_task_obj.edit_time.strftime(
                            PipelineTemplateWebWrapper.SERIALIZE_DATE_FORMAT
                        ),
                        "create_time": clocked_task_obj.create_time.strftime(
                            PipelineTemplateWebWrapper.SERIALIZE_DATE_FORMAT
                        ),
                        "editor": clocked_task_obj.editor,
                        "creator": clocked_task_obj.creator,
                    }
                )
            result["clocked_task"] = clocked_tasks

        if not kwargs.get("export_template_scheme"):
            # 将不需要导出的执行方案移除
            for pipeline_template_info in pipeline_temp_data["template"].values():
                pipeline_template_info.pop("schemes", None)

        return result

    def import_operation_check(self, template_data):

        template = template_data["template"]
        pipeline_template = template_data["pipeline_template_data"]["template"]

        new_template = []
        for tmpl in list(template.values()):
            str_id = tmpl["pipeline_template_str_id"]
            pipeline = pipeline_template[str_id]
            new_template.append({"id": tmpl["id"], "name": pipeline["name"]})

        override_template = []
        existed_templates = self.filter(pk__in=list(template.keys()), is_deleted=False).select_related(
            "pipeline_template"
        )
        for tmpl in existed_templates:
            override_template.append(
                {"id": tmpl.id, "name": tmpl.pipeline_template.name, "template_id": tmpl.pipeline_template.template_id}
            )

        result = {"can_override": True, "new_template": new_template, "override_template": override_template}
        return result

    def _perform_import(self, template_data, check_info, override, defaults_getter, operator):
        template = template_data["template"]
        tid_to_reuse = {}

        # find old template_id for override using
        # import_id -> reuse_id
        for template_to_be_replaced in check_info["override_template"]:
            task_template_id = template_to_be_replaced["id"]
            # pipeline_template_id
            template_id = template_data["template"][str(task_template_id)]["pipeline_template_str_id"]
            tid_to_reuse[template_id] = template_to_be_replaced["template_id"]

        # import pipeline template first
        id_map = PipelineTemplateWebWrapper.import_templates(
            template_data["pipeline_template_data"], override=override, tid_to_reuse=tid_to_reuse
        )
        old_id_to_new_id = id_map[PipelineTemplateWebWrapper.ID_MAP_KEY]

        # 多版本子流程兼容：同一子流程被多个父流程按不同版本引用时，pipeline 层会为其生成两个导出键
        # （原始 template_id 与版本专属 uniqid），但业务层按 template_id 去重只会生成一条业务记录，
        # 导致其中一个版本的 PipelineTemplate 在导入后成为孤儿（无对应业务记录），
        # 后续展示/创建任务走 replace_template_id(reverse=True) 时会 .get() 抛 DoesNotExist 而 500。
        # 这里为孤儿 PipelineTemplate 补齐对应的业务记录（拷贝同原始 template_id 的兄弟业务记录）。
        pipeline_export_keys = set(template_data["pipeline_template_data"]["template"].keys())
        business_export_keys = {td["pipeline_template_str_id"] for td in template.values()}
        orphan_export_keys = pipeline_export_keys - business_export_keys
        if orphan_export_keys:
            source_by_original_id = {}
            for td in template.values():
                source_by_original_id.setdefault(td["pipeline_template_id"], td)
            for orphan_key in orphan_export_keys:
                pipeline_info = template_data["pipeline_template_data"]["template"][orphan_key]
                source = source_by_original_id.get(pipeline_info["template_id"])
                if source is None:
                    # 正常情况下孤儿导出键必然能通过 template_id 找到同源的兄弟业务记录；找不到说明导出数据
                    # 不完整或已损坏。此处不做静默跳过（会得到不完整的导入结果，后续展示/执行时再报 500），
                    # 直接返回明确错误给前端，便于定位问题。
                    message = _(
                        "流程导入失败: 导出数据中的子流程(export_key={export_key}, template_id={template_id})"
                        "找不到对应的原始业务记录, 导出文件可能已损坏或不完整 | _perform_import"
                    ).format(export_key=orphan_key, template_id=pipeline_info["template_id"])
                    logger.error(message)
                    return {
                        "result": False,
                        "message": message,
                        "data": None,
                        "code": err_code.UNKNOWN_ERROR.code,
                    }
                orphan_dict = copy.deepcopy(source)
                orphan_dict["pipeline_template_str_id"] = orphan_key
                template[orphan_key] = orphan_dict
                # 让导入确认/结果展示也能感知到这条新流程
                check_info["new_template"].append(
                    {"id": orphan_key, "name": pipeline_info.get("name", source.get("name", ""))}
                )

        new_objects = []
        new_objects_template_ids = set()

        # find templates which had been deleted
        if override:
            # template 的键可能包含非数字的导出键（多版本子流程孤儿），过滤掉避免 id__in 查询报错
            numeric_keys = [k for k in template.keys() if str(k).isdigit()]
            new_objects_template_ids = set(
                self.model.objects.filter(id__in=numeric_keys, is_deleted=True).values_list(
                    "pipeline_template_id", flat=True
                )
            )

        new_pipeline_template_id__old_tid_map = {}
        for tid, template_dict in list(template.items()):
            new_pipeline_template_id = old_id_to_new_id[template_dict["pipeline_template_str_id"]]
            new_pipeline_template_id__old_tid_map[new_pipeline_template_id] = tid
            template_dict["pipeline_template_id"] = new_pipeline_template_id
            defaults = defaults_getter(template_dict)
            # use update or create to avoid id conflict
            # 孤儿导出键为非数字，无法作为业务主键复用，覆盖模式下也无既有业务记录可复用，直接新建
            if override and str(tid).isdigit():
                obj, created = self.update_or_create(id=tid, defaults=defaults)
                if created:
                    new_objects_template_ids.add(template_dict["pipeline_template_id"])
            else:
                if override:
                    self.model.objects.create(**defaults)
                    new_objects_template_ids.add(template_dict["pipeline_template_id"])
                else:
                    new_objects.append(self.model(**defaults))
                    new_objects_template_ids.add(template_dict["pipeline_template_id"])

        # update creator when templates are created
        PipelineTemplate.objects.filter(template_id__in=new_objects_template_ids).update(creator=operator)

        # update flows map
        flows = {info["id"]: info["name"] for info in check_info["new_template"]}

        if not override:
            self.model.objects.bulk_create(new_objects)

            create_templates = list(self.model.objects.filter(pipeline_template_id__in=new_objects_template_ids))

            # create flows map
            flows = {tmp.id: tmp.name for tmp in create_templates}

            # send_signal
            if create_templates:
                batch_create.send(self.model, instance=create_templates, creator=operator)

        template_recreated_info = defaultdict(dict)
        template_source_type = PROJECT if self.model.__name__ == "TaskTemplate" else COMMON
        created_template_objs = self.model.objects.filter(
            pipeline_template_id__in=new_pipeline_template_id__old_tid_map.keys()
        )

        # 建立新老流程模板的映射关系
        # 保留 template_source_type 的原因：后续导入项目流程所依赖的「公共流程」，可能不再以项目流程的方式导入，预留区分
        for created_template_obj in created_template_objs:
            new_tid = created_template_obj.id
            old_tid = new_pipeline_template_id__old_tid_map[created_template_obj.pipeline_template_id]
            template_recreated_info[template_source_type][old_tid] = {
                "id": new_tid,
                "export_data": template[old_tid],
                "import_data": {
                    "id": new_tid,
                    "name": created_template_obj.name,
                    "pipeline_template_id": created_template_obj.pipeline_template_id,
                },
            }

        id_map["template_recreated_info"] = template_recreated_info

        return {
            "result": True,
            "data": {"count": len(template), "flows": flows},
            "id_map": id_map,
            "message": "Successfully imported %s flows" % len(template),
            "code": err_code.SUCCESS.code,
        }

    def check_templates_subprocess_expired(self, tmpl_and_pipeline_id):
        # fetch all template relationship in template_ids
        pipeline_tmpl_ids = [item["pipeline_template_id"] for item in tmpl_and_pipeline_id]
        subproc_infos = TemplateRelationship.objects.filter(ancestor_template_id__in=pipeline_tmpl_ids)

        # get all subprocess reference template's version
        subproc_templ = [info.descendant_template_id for info in subproc_infos]
        tmpl_versions = TemplateCurrentVersion.objects.filter(template_id__in=subproc_templ)

        # comparison data prepare
        tmpl_version_map = {ver.template_id: ver.current_version for ver in tmpl_versions}
        tmpl_id_map = {item["pipeline_template_id"]: item["id"] for item in tmpl_and_pipeline_id}

        # compare
        subproc_expired_templ = set()
        for info in subproc_infos:
            if info.descendant_template_id not in tmpl_version_map or info.always_use_latest:
                continue
            if info.version != tmpl_version_map.get(info.descendant_template_id):
                subproc_expired_templ.add(info.ancestor_template_id)

        return [tmpl_id_map[pid] for pid in subproc_expired_templ]


class BaseTemplate(models.Model):
    """
    @summary: base abstract template，without containing business info
    """

    category = models.CharField(_("模板类型"), choices=TASK_CATEGORY, max_length=255, default="Default")
    pipeline_template = models.ForeignKey(
        PipelineTemplate, blank=True, null=True, on_delete=models.SET_NULL, to_field="template_id"
    )
    collector = models.ManyToManyField(settings.AUTH_USER_MODEL, verbose_name=_("收藏模板的人"), blank=True)
    notify_type = models.CharField(_("流程事件通知方式"), max_length=128, default="[]")
    # 形如 json.dumps({'receiver_group': ['Maintainers'], 'more_receiver': 'username1,username2'})
    notify_receivers = models.TextField(_("流程事件通知人"), default="{}")
    time_out = models.IntegerField(_("流程超时时间(分钟)"), default=20)
    is_deleted = models.BooleanField(_("是否删除"), default=False)
    ai_notify_type = models.JSONField(_("AI分析个人通知方式"), default=dict)
    ai_notify_group = models.JSONField(_("AI分析群聊通知配置"), default=dict)

    class Meta:
        # abstract would not be inherited automatically
        abstract = True
        ordering = ["-id"]

    def delete(self, real_delete=False):
        if real_delete:
            return super().delete()
        setattr(self, "is_deleted", True)
        self.save()

    @property
    def category_name(self):
        return self.get_category_display()

    @property
    def creator(self):
        return self.pipeline_template.creator

    @property
    def creator_name(self):
        return convert_readable_username(self.pipeline_template.creator)

    @property
    def editor_name(self):
        if self.pipeline_template and self.pipeline_template.editor:
            return convert_readable_username(self.pipeline_template.editor)
        else:
            return ""

    @property
    def name(self):
        return self.pipeline_template.name if self.pipeline_template else ""

    @property
    def create_time(self):
        return self.pipeline_template.create_time

    @property
    def edit_time(self):
        return self.pipeline_template.edit_time or self.create_time

    @property
    def pipeline_tree(self):
        tree = self.pipeline_template.data
        replace_template_id(self.__class__, tree, reverse=True)
        # add nodes attr
        pipeline_web_clean = PipelineWebTreeCleaner(tree)
        nodes = NodeInTemplate.objects.filter(template_id=self.pipeline_template.template_id, version=self.version)
        nodes_attr = NodeAttr.get_nodes_attr(nodes, "template")
        pipeline_web_clean.to_web(nodes_attr)
        return tree

    @property
    def template_id(self):
        return self.id

    @property
    def subprocess_info(self):
        info = self.pipeline_template.subprocess_version_info
        pipeline_temp_ids = [item["descendant_template_id"] for item in info["details"]]
        templates = fetch_templates_info(
            pipeline_temp_ids,
            fetch_fields=("id", "pipeline_template_id"),
            appointed_template_type=COMMON if self.__class__.__name__ == "CommonTemplate" else None,
        )
        pid_to_tid = {item["pipeline_template_id"]: item["id"] for item in templates}
        for subprocess_info in info["details"]:
            subprocess_info["template_id"] = pid_to_tid[subprocess_info.pop("descendant_template_id")]

        return info

    @property
    def version(self):
        return self.pipeline_template.version

    @property
    def subprocess_has_update(self):
        return self.pipeline_template.subprocess_has_update

    @property
    def template_wrapper(self):
        return PipelineTemplateWebWrapper(self.pipeline_template)

    @property
    def has_subprocess(self):
        return self.pipeline_template.has_subprocess

    def referencer(self):
        pipeline_template_referencer = self.pipeline_template.referencer()
        if not pipeline_template_referencer:
            return []

        task_template_cls = apps.get_model("tasktmpl3", "TaskTemplate")
        task_template_qs = task_template_cls.objects.filter(
            pipeline_template_id__in=pipeline_template_referencer, is_deleted=False
        ).values("id", "pipeline_template__name", "project__id", "project__name")
        result = [
            {
                "template_type": PROJECT,
                "id": template_info["id"],
                "name": template_info["pipeline_template__name"],
                "project_id": template_info["project__id"],
                "project_name": template_info["project__name"],
            }
            for template_info in task_template_qs
        ]

        if self.__class__.__name__ == "CommonTemplate":
            common_template_qs = self.__class__.objects.filter(
                pipeline_template_id__in=pipeline_template_referencer, is_deleted=False
            ).values("id", "pipeline_template__name", "extra_info")
            result.extend(
                [
                    {
                        "template_type": COMMON,
                        "id": template_info["id"],
                        "name": template_info["pipeline_template__name"],
                        "project_scope": template_info["extra_info"]["project_scope"],
                    }
                    for template_info in common_template_qs
                ]
            )
        return result

    def referencer_appmaker(self):
        if not hasattr(self, "appmaker_set"):
            return []

        appmaker_referencer = self.appmaker_set.filter(is_deleted=False).values("id", "name")
        if not appmaker_referencer.exists():
            return []

        return appmaker_referencer

    def referencer_clocked_task(self):
        clocked_task_referencer = ClockedTask.objects.filter(
            template_id=self.id, state=CLOCKED_TASK_NOT_STARTED
        ).values("id", "task_name")
        return [{"id": referencer["id"], "name": referencer["task_name"]} for referencer in clocked_task_referencer]

    def referencer_periodic_task(self):
        periodic_task_cls = apps.get_model("periodictask", "PeriodicTask")
        periodic_task_referencer = periodic_task_cls.objects.filter(template_id=self.id).values("id", "task__name")
        return [{"id": referencer["id"], "name": referencer["task__name"]} for referencer in periodic_task_referencer]

    def get_clone_pipeline_tree(self):
        clone_tree = self.pipeline_template.clone_data()
        replace_template_id(self.__class__, clone_tree, reverse=True)
        return clone_tree

    def get_form(self, version=None):
        return self.template_wrapper.get_form(version)

    def get_outputs(self, version=None):
        return self.template_wrapper.get_outputs(version)

    def user_collect(self, username, method):
        user_model = get_user_model()
        user = user_model.objects.get(username=username)
        if method == "add":
            self.collector.add(user)
        else:
            self.collector.remove(user)
        self.save()
        return {"result": True, "data": ""}

    def get_pipeline_tree_by_version(self, version=None):
        tree = self.pipeline_template.data_for_version(version)
        replace_template_id(self.__class__, tree, reverse=True)
        # add nodes attr
        pipeline_web_clean = PipelineWebTreeCleaner(tree)
        nodes = NodeInTemplate.objects.filter(template_id=self.pipeline_template.template_id, version=self.version)
        nodes_attr = NodeAttr.get_nodes_attr(nodes, "template")
        pipeline_web_clean.to_web(nodes_attr)
        return tree


class DefaultTemplateScheme(models.Model):
    project_id = models.IntegerField(default=-1, help_text="项目ID，-1代表公共流程")
    template_id = models.IntegerField(help_text="流程ID")
    default_scheme_ids = models.TextField(help_text="默认执行方案组合ID拼接结果，用`,`分隔", null=True, blank=True)

    class Meta:
        verbose_name = "默认执行方案"
        unique_together = ("project_id", "template_id")

# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import logging

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model

from pipeline.parser.utils import replace_all_id

from gcloud import err_code
from gcloud.constants import TEMPLATE_EXPORTER_SOURCE_PROJECT
from gcloud.commons.template.models import BaseTemplate, BaseTemplateManager
from gcloud.core.models import Project
from gcloud.tasktmpl3.mixins import TaskTmplStatisticsMixin

logger = logging.getLogger("root")


class TaskTemplateManager(BaseTemplateManager, TaskTmplStatisticsMixin):
    def create(self, **kwargs):
        pipeline_template = self.create_pipeline_template(**kwargs)
        task_template = self.model(
            project=kwargs["project"],
            category=kwargs["category"],
            pipeline_template=pipeline_template,
            notify_type=kwargs["notify_type"],
            notify_receivers=kwargs["notify_receivers"],
            time_out=kwargs["time_out"],
        )
        task_template.save()
        return task_template

    def export_templates(self, template_id_list, project_id):
        if self.filter(id__in=template_id_list, project_id=project_id).count() != len(template_id_list):
            raise self.model.DoesNotExist("{}(id={}) does not exist.".format(self.model.__name__, template_id_list))
        data = super(TaskTemplateManager, self).export_templates(template_id_list)
        data["template_source"] = TEMPLATE_EXPORTER_SOURCE_PROJECT
        return data

    def import_operation_check(self, template_data, project_id):
        data = super(TaskTemplateManager, self).import_operation_check(template_data)

        template = template_data["template"]

        relate_project_ids = self.filter(id__in=list(template.keys()), is_deleted=False).values_list(
            "project_id", flat=True
        )
        is_multiple_relate = len(set(relate_project_ids)) > 1
        is_across_override = relate_project_ids and relate_project_ids[0] != int(project_id)
        has_common_template = not all([tmpl.get("project_id") for _, tmpl in list(template_data["template"].items())])

        can_override = not (is_multiple_relate or is_across_override or has_common_template)

        # 以文件中设定的禁止覆盖设定为最高优先级
        if template_data.get("override_forbidden", False):
            can_override = False

        if not can_override:
            data["override_template"] = []

        result = {
            "can_override": can_override,
            "new_template": data["new_template"],
            "override_template": data["override_template"],
        }
        return result

    def import_templates(self, template_data, override, project_id, operator=None):
        project = Project.objects.get(id=project_id)
        check_info = self.import_operation_check(template_data, project_id)

        # operation validation check
        if override and (not check_info["can_override"]):
            return {
                "result": False,
                "message": "Unable to override flows across project",
                "data": 0,
                "code": err_code.INVALID_OPERATION.code,
            }

        def defaults_getter(template_dict):
            return {
                "project": project,
                "category": template_dict["category"],
                "notify_type": template_dict["notify_type"],
                "notify_receivers": template_dict["notify_receivers"],
                "time_out": template_dict["time_out"],
                "pipeline_template_id": template_dict["pipeline_template_id"],
                "is_deleted": False,
            }

        return super(TaskTemplateManager, self)._perform_import(
            template_data=template_data,
            check_info=check_info,
            override=override,
            defaults_getter=defaults_getter,
            operator=operator,
        )

    def replace_all_template_tree_node_id(self):
        templates = self.filter(is_deleted=False)
        success = 0
        for template in templates:
            tree_data = template.pipeline_template.data
            try:
                replace_all_id(tree_data)
            except Exception:
                continue
            template.pipeline_template.update_template(tree_data)
            success += 1
        return len(templates), success

    def get_collect_template(self, project_id, username):
        user_model = get_user_model()
        collected_templates = user_model.objects.get(username=username).tasktemplate_set.values_list("id", flat=True)
        collected_templates_list = []
        template_list = self.filter(is_deleted=False, project_id=project_id, id__in=list(collected_templates))
        for template in template_list:
            collected_templates_list.append({"id": template.id, "name": template.name})
        return True, collected_templates_list

    def get_templates_with_expired_subprocess(self, project_id):
        tmpl_and_pipeline_id = self.filter(project_id=project_id, is_deleted=False).values("id", "pipeline_template_id")
        return self.check_templates_subprocess_expired(tmpl_and_pipeline_id)


class TaskTemplate(BaseTemplate):
    project = models.ForeignKey(Project, verbose_name=_("所属项目"), null=True, blank=True, on_delete=models.SET_NULL)
    executor_proxy = models.CharField(_("任务执行人代理"), max_length=255, default="", blank=True)

    objects = TaskTemplateManager()

    def __unicode__(self):
        return "%s_%s" % (self.project, self.pipeline_template)

    class Meta(BaseTemplate.Meta):
        verbose_name = _("流程模板 TaskTemplate")
        verbose_name_plural = _("流程模板 TaskTemplate")

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

import base64
import logging

from django.db import models
from django.db.models import Count
from django.utils.translation import ugettext_lazy as _

from blueapps.utils import managermixins

from iam import Resource, Subject, Action
from iam.shortcuts import allow_or_raise_auth_failed

from gcloud.conf import settings
from gcloud.core.api_adapter import (
    create_maker_app,
    edit_maker_app,
    del_maker_app,
    modify_app_logo,
    get_app_logo_url,
)
from gcloud.core.constant import AE
from gcloud.core.models import Project
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.utils.dates import time_now_str
from gcloud.core.utils import convert_readable_username
from gcloud.utils.strings import name_handler

from gcloud.iam_auth import IAMMeta
from gcloud.iam_auth import get_iam_client

logger = logging.getLogger("root")
iam = get_iam_client()


class AppMakerManager(models.Manager, managermixins.ClassificationCountMixin):
    def save_app_maker(self, project_id, app_params, fake=False):
        """
        @summary:
        @param project_id: 项目 ID
        @param app_params: App maker参数
        @param fake: 为True则不会真正调用API创建轻应用
        @return:
        """
        logger.info("save_app_maker params: %s" % app_params)
        app_id = app_params["id"]
        if app_id == "0" or not app_id:
            app_id = None
        template_id = app_params["template_id"]
        app_params["name"] = name_handler(app_params["name"], 20)
        app_params["desc"] = name_handler(app_params.get("desc", ""), 30)
        proj = Project.objects.get(id=project_id)
        try:
            task_template = TaskTemplate.objects.get(pk=template_id, project_id=project_id, is_deleted=False)
        except TaskTemplate.DoesNotExist:
            return False, _("保存失败，引用的流程模板不存在！")

        if not app_id:
            subject = Subject("user", app_params["username"])
            action = Action(IAMMeta.FLOW_CREATE_MINI_APP_ACTION)
            resources = [
                Resource(
                    IAMMeta.SYSTEM_ID,
                    IAMMeta.FLOW_RESOURCE,
                    str(task_template.id),
                    {"iam_resource_owner": task_template.creator, "name": task_template.name},
                )
            ]

            allow_or_raise_auth_failed(
                iam=iam, system=IAMMeta.SYSTEM_ID, subject=subject, action=action, resources=resources
            )

            fields = {
                "project": proj,
                "name": app_params["name"],
                "code": "",
                "desc": app_params["desc"],
                "logo_url": "",
                "link": app_params["link_prefix"],
                "creator": app_params["username"],
                "editor": app_params["username"],
                "task_template": task_template,
                # 生成一个删除状态的对象，以便拼接轻应用访问链接
                "is_deleted": True,
            }
            if app_params.get("template_scheme_id"):
                fields["template_scheme_id"] = app_params["template_scheme_id"]
            app_maker_obj = AppMaker.objects.create(**fields)

            # update app link
            app_id = app_maker_obj.id
            app_link = "{appmaker_prefix}{app_id}/newtask/{project_id}/selectnode/?template_id={template_id}".format(
                appmaker_prefix=app_params["link_prefix"], app_id=app_id, project_id=project_id, template_id=template_id
            )
            app_maker_obj.link = app_link

            if fake:
                app_maker_obj.code = "%s%s" % (settings.APP_CODE, time_now_str())
                app_maker_obj.is_deleted = False
                app_maker_obj.save()
                return True, app_maker_obj

            # create app on blueking desk
            app_create_result = create_maker_app(
                app_params["username"],
                app_params["name"],
                app_link,
                app_params["username"],
                task_template.category,
                app_params["desc"],
            )
            if not app_create_result["result"]:
                return False, _("创建轻应用失败：%s") % app_create_result["message"]

            app_code = app_create_result["data"]["bk_light_app_code"]
            app_maker_obj.code = app_code
            app_maker_obj.is_deleted = False

        # edit appmaker
        else:
            try:
                app_maker_obj = AppMaker.objects.get(
                    id=app_id, project_id=project_id, task_template__id=template_id, is_deleted=False
                )
            except AppMaker.DoesNotExist:
                return False, _("保存失败，当前操作的轻应用不存在或已删除！")

            subject = Subject("user", app_params["username"])
            action = Action(IAMMeta.MINI_APP_EDIT_ACTION)
            resources = [
                Resource(
                    IAMMeta.SYSTEM_ID,
                    IAMMeta.MINI_APP_RESOURCE,
                    str(app_maker_obj.id),
                    {"iam_resource_owner": app_maker_obj.creator, "name": app_maker_obj.name},
                )
            ]

            allow_or_raise_auth_failed(
                iam=iam, system=IAMMeta.SYSTEM_ID, subject=subject, action=action, resources=resources
            )

            app_code = app_maker_obj.code
            creator = app_maker_obj.creator
            link = app_maker_obj.link

            if not fake:
                # edit app on blueking
                app_edit_result = edit_maker_app(
                    creator, app_code, app_params["name"], link, creator, task_template.category, app_params["desc"],
                )
                if not app_edit_result["result"]:
                    return False, _("编辑轻应用失败：%s") % app_edit_result["message"]

            app_maker_obj.name = app_params["name"]
            app_maker_obj.desc = app_params["desc"]
            app_maker_obj.editor = app_params["username"]
            if "template_scheme_id" in app_params:
                app_maker_obj.template_scheme_id = app_params["template_scheme_id"]

        # upload app logo
        if not fake and app_params["logo_content"]:
            logo = base64.b64encode(app_params["logo_content"])
            app_logo_result = modify_app_logo(app_maker_obj.creator, app_code, logo)
            if not app_logo_result["result"]:
                logger.warning(
                    "AppMaker[id=%s] upload logo failed: %s" % (app_maker_obj.id, app_logo_result["message"])
                )
            # update app maker info
            app_maker_obj.logo_url = get_app_logo_url(app_code=app_code)

        app_maker_obj.save()
        return True, app_maker_obj

    def del_app_maker(self, project_id, app_id, fake=False):
        """
        @param app_id:
        @param project_id:
        @param fake:
        @return:
        """
        try:
            app_maker_obj = AppMaker.objects.get(id=app_id, project_id=project_id, is_deleted=False)
        except AppMaker.DoesNotExist:
            return False, _("当前操作的轻应用不存在或已删除！")

        del_name = time_now_str()
        if not fake:
            # rename before delete to avoid name conflict when create a new app
            app_edit_result = edit_maker_app(app_maker_obj.creator, app_maker_obj.code, del_name[:20],)
            if not app_edit_result["result"]:
                return False, _("删除失败：%s") % app_edit_result["message"]

            # delete app on blueking desk
            app_del_result = del_maker_app(app_maker_obj.creator, app_maker_obj.code)
            if not app_del_result["result"]:
                return False, _("删除失败：%s") % app_del_result["message"]

        app_maker_obj.is_deleted = True
        app_maker_obj.name = del_name[:20]
        app_maker_obj.save()
        return True, app_maker_obj.code

    def group_by_project_id(self, appmaker, group_by):
        # 按起始时间、业务（可选）查询各类型轻应用个数和占比√(echarts)
        total = appmaker.count()
        appmaker_list = appmaker.values(AE.project_id, AE.project__name).annotate(value=Count(group_by)).order_by()
        groups = []
        for data in appmaker_list:
            groups.append(
                {"code": data.get(AE.project_id), "name": data.get(AE.project__name), "value": data.get("value", 0)}
            )
        return total, groups

    def group_by_category(self, appmaker, group_by):
        # 按起始时间、类型（可选）查询各业务下新增轻应用个数（排序）
        # field 用于外键查询对应的类型内容
        field = "task_template__%s" % group_by
        total = appmaker.count()
        # 获取choices字段
        choices = TaskTemplate.objects.get_choices(group_by)
        appmaker_list = appmaker.values(field).annotate(value=Count(field)).order_by()
        values = {item[field]: item["value"] for item in appmaker_list}
        groups = []
        for code, name in choices:
            groups.append({"code": code, "name": name, "value": values.get(code, 0)})
        return total, groups


class AppMaker(models.Model):
    """
    APP maker的基本信息
    """

    project = models.ForeignKey(Project, verbose_name=_("所属项目"), null=True, on_delete=models.SET_NULL)
    name = models.CharField(_("APP名称"), max_length=255)
    code = models.CharField(_("APP编码"), max_length=255)
    info = models.CharField(_("APP基本信息"), max_length=255, null=True)
    desc = models.CharField(_("APP描述信息"), max_length=255, null=True)
    logo_url = models.TextField(_("轻应用logo存放地址"), default="", blank=True)
    link = models.URLField(_("gcloud链接"), max_length=255)
    creator = models.CharField(_("创建人"), max_length=100)
    create_time = models.DateTimeField(_("创建时间"), auto_now_add=True)
    editor = models.CharField(_("编辑人"), max_length=100, null=True)
    edit_time = models.DateTimeField(_("编辑时间"), auto_now=True, null=True)
    task_template = models.ForeignKey(TaskTemplate, verbose_name=_("关联模板"))
    template_scheme_id = models.CharField(_("执行方案"), max_length=100, blank=True)
    is_deleted = models.BooleanField(_("是否删除"), default=False)

    objects = AppMakerManager()

    @property
    def creator_name(self):
        return convert_readable_username(self.creator)

    @property
    def editor_name(self):
        return convert_readable_username(self.editor)

    @property
    def task_template_name(self):
        return self.task_template.name

    @property
    def category(self):
        return self.task_template.category

    def __unicode__(self):
        return "%s_%s" % (self.project, self.name)

    class Meta:
        verbose_name = _("轻应用 AppMaker")
        verbose_name_plural = _("轻应用 AppMaker")
        ordering = ["-id"]

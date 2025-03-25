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
import datetime
import typing
from os import environ

import pytz
from django.conf import settings
from django.contrib.auth.models import Group
from django.db import models, transaction
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from gcloud.constants import TEMPLATE_SOURCE


class BusinessManager(models.Manager):
    def supplier_account_for_business(self, cc_id):
        return self.get(cc_id=cc_id).cc_owner

    def supplier_id_for_business(self, cc_id):
        return self.get(cc_id=cc_id).cc_company or 0


class Business(models.Model):
    cc_id = models.IntegerField(unique=True)
    cc_name = models.CharField(max_length=256)
    # 开发商账号 bk_supplier_account
    cc_owner = models.CharField(max_length=100)
    # 开发商ID bk_supplier_id
    cc_company = models.CharField(max_length=100)
    time_zone = models.CharField(max_length=100, blank=True)
    life_cycle = models.CharField(_("生命周期"), max_length=100, blank=True)
    executor = models.CharField(_("任务执行者"), max_length=100, blank=True)
    # null 表未归档，disabled 表示已归档
    status = models.CharField(_("业务状态"), max_length=32, null=True)
    always_use_executor = models.BooleanField(_("是否始终使用任务执行者"), default=False)
    tenant_id = models.CharField(_("租户ID"), default="default", max_length=64, db_index=True)

    groups = models.ManyToManyField(Group, through="BusinessGroupMembership")

    objects = BusinessManager()

    # LifeCycle：'1'：测试中， '2'：已上线， '3'： 停运， 其他如'0'、''是历史遗留非法值，暂时认为是已上线状态
    LIFE_CYCLE_TESTING = "1"  # 测试中
    LIFE_CYCLE_ONLINE = "2"  # 已上线
    LIFE_CYCLE_CLOSE_DOWN = "3"  # 停运

    class Meta:
        verbose_name = _("业务 Business")
        verbose_name_plural = _("业务 Business")
        permissions = (
            ("get_business", "Can get business"),
            ("manage_business", "Can manage business"),
        )

    def __unicode__(self):
        return "%s_%s" % (self.cc_id, self.cc_name)

    def __str__(self):
        return "%s_%s" % (self.cc_id, self.cc_name)

    def available(self):
        return self.status != "disabled"


class UserBusiness(models.Model):
    """
    用户默认业务表
    """

    user = models.CharField(_("用户QQ"), max_length=255, unique=True)
    default_buss = models.IntegerField(_("默认业务"))

    def __unicode__(self):
        return "%s_%s" % (self.user, self.default_buss)

    class Meta:
        verbose_name = _("用户默认业务 UserBusiness")
        verbose_name_plural = _("用户默认业务 UserBusiness")


class BusinessGroupMembership(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

    date_created = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = _("业务用户组 BusinessGroupMembership")
        verbose_name_plural = _("业务用户组 BusinessGroupMembership")
        unique_together = ("business", "group")

    def __unicode__(self):
        return "B%s:G%s" % (self.business_id, self.group_id)

    def __str__(self):
        return "B%s:G%s" % (self.business_id, self.group_id)


class EnvVarManager(models.Manager):
    def get_var(self, key, default=None):
        objs = self.filter(key=key)
        if objs.exists():
            return objs[0].value
        return environ.get(key, default)


class EnvironmentVariables(models.Model):
    key = models.CharField(_("变量KEY"), max_length=255, unique=True)
    name = models.CharField(_("变量描述"), max_length=255, blank=True)
    value = models.CharField(_("变量值"), max_length=1000, blank=True)

    objects = EnvVarManager()

    def __unicode__(self):
        return "%s_%s" % (self.key, self.name)

    def __str__(self):
        return "%s_%s" % (self.key, self.name)

    class Meta:
        verbose_name = _("环境变量 EnvironmentVariables")
        verbose_name_plural = _("环境变量 EnvironmentVariables")


RESOURCE_CONFIG_TYPES = [
    ("set", _("集群筛选配置")),
    ("host", _("主机筛选配置")),
]


class ResourceConfig(models.Model):
    """
    资源筛选配置方案，包括集群资源和主机资源的筛选配置方案
    """

    project_id = models.IntegerField(_("项目 ID"))
    name = models.CharField(_("配置名称"), max_length=255, help_text=_("每个项目下的配置名称要保证唯一"))
    config_type = models.CharField(_("配置类型"), max_length=255, choices=RESOURCE_CONFIG_TYPES)
    creator = models.CharField(_("创建者"), max_length=255, null=True, blank=True)
    data = models.TextField(_("筛选配置参数"), default="{}")
    create_time = models.DateTimeField(_("最近编辑时间"), auto_now_add=True, null=True)

    class Meta:
        verbose_name = _("集群资源筛选方案")
        verbose_name_plural = _("集群资源筛选方案")
        unique_together = ("project_id", "name", "config_type")
        ordering = ["-id"]

    @property
    def config_type_name(self):
        return self.get_config_type_display()

    def __str__(self):
        return self.name


class ProjectManager(models.Manager):
    def sync_project_from_cmdb_business(self, businesses):
        with transaction.atomic():
            if not businesses:
                return

            exist_sync_cc_id = set(self.filter(from_cmdb=True).values_list("bk_biz_id", flat=True))
            to_be_sync_cc_id = set(businesses.keys()) - exist_sync_cc_id
            projects = []

            # update exist business project
            exist_projects = self.all()
            for exist_project in exist_projects:
                business = businesses.get(exist_project.bk_biz_id)
                if not business:
                    continue

                if exist_project.name != business["cc_name"] or exist_project.time_zone != business["time_zone"]:
                    exist_project.name = business["cc_name"]
                    exist_project.time_zone = business["time_zone"]
                    exist_project.save()

            for cc_id in to_be_sync_cc_id:
                biz = businesses[cc_id]
                projects.append(
                    Project(
                        name=biz["cc_name"],
                        time_zone=biz["time_zone"],
                        creator=biz["creator"],
                        desc="",
                        from_cmdb=True,
                        bk_biz_id=cc_id,
                        tenant_id=biz["tenant_id"],
                    )
                )
            # maybe have duplicate entry, caller function should cope with the exception
            self.bulk_create(projects, batch_size=5000)

    def update_business_project_status(self, archived_cc_ids, active_cc_ids):
        self.filter(bk_biz_id__in=archived_cc_ids, from_cmdb=True).update(is_disable=True)
        self.filter(bk_biz_id__in=active_cc_ids, from_cmdb=True).update(is_disable=False)

    def get_timezone_based_timestamp(self, project_id, timestamp_fmt="%Y%m%d%H%M%S"):
        project_tz = getattr(self.filter(id=project_id).first(), "time_zone") or settings.TIME_ZONE
        timestamp = datetime.datetime.now(tz=pytz.timezone(project_tz)).strftime(timestamp_fmt)
        return timestamp


class Project(models.Model):
    name = models.CharField(_("项目名"), max_length=192)
    time_zone = models.CharField(_("项目时区"), max_length=100, blank=True)
    creator = models.CharField(_("创建者"), max_length=256)
    desc = models.CharField(_("项目描述"), max_length=512, blank=True)
    create_at = models.DateTimeField(_("创建时间"), auto_now_add=True)
    from_cmdb = models.BooleanField(_("是否是从 CMDB 业务同步过来的项目"), default=False)
    bk_biz_id = models.IntegerField(_("业务同步项目对应的 CMDB 业务 ID"), default=-1)
    is_disable = models.BooleanField(_("是否已停用"), default=False)
    relate_business = models.ManyToManyField(verbose_name=_("关联项目"), to=Business, blank=True)
    tenant_id = models.CharField(_("租户ID"), default="default", max_length=64, db_index=True)

    objects = ProjectManager()

    class Meta:
        verbose_name = _("项目 Project")
        verbose_name_plural = _("项目 Project")
        unique_together = ("bk_biz_id", "name")

    def __unicode__(self):
        return "%s_%s" % (self.id, self.name)

    def __str__(self):
        return "%s_%s" % (self.id, self.name)


class ProjectBasedComponentManager(models.Manager):
    def get_components(self):
        return self.values_list("component_code", flat=True)

    def get_components_of_other_projects(self, project_id):
        pre_exclude_components = self.exclude(project_id=project_id).values_list("component_code", flat=True)
        project_components = self.filter(project_id=project_id).values_list("component_code", flat=True)
        return list(set(pre_exclude_components) - set(project_components))


class ProjectBasedComponent(models.Model):
    """
    相关插件默认对所有人不显示，只在配置的项目中进行显示
    """

    component_code = models.CharField(_("组件编码"), max_length=255)
    project_id = models.CharField(_("项目id"), max_length=64)

    objects = ProjectBasedComponentManager()

    class Meta:
        verbose_name = _("基于项目的组件 ProjectBasedComponent")
        verbose_name_plural = _("基于项目的组件 ProjectBasedComponent")


class DisabledComponentManager(models.Manager):
    def get_disabled_components(self, scope: str, action: str) -> typing.List[str]:
        disabled_components: typing.List[str] = self.filter(
            Q(scope=DisabledComponent.SCOPE_TYPE_ALL, action=DisabledComponent.ACTION_TYPE_ALL)
            | Q(scope=DisabledComponent.SCOPE_TYPE_ALL, action=action)
            | Q(action=DisabledComponent.ACTION_TYPE_ALL, scope=scope)
            | Q(scope=scope, action=action)
        ).values_list("component_code", flat=True)

        return list(disabled_components)


class DisabledComponent(models.Model):
    """
    禁用的插件
    """

    ACTION_TYPE_LIST = "list"
    ACTION_TYPE_RETRIEVE = "retrieve"
    ACTION_TYPE_ALL = "all"
    SCOPE_TYPE_TASK = "task"
    SCOPE_TYPE_FLOW = "flow"
    SCOPE_TYPE_ALL = "all"

    ACTION_CHOICES = [
        (ACTION_TYPE_LIST, ACTION_TYPE_LIST),
        (ACTION_TYPE_RETRIEVE, ACTION_TYPE_RETRIEVE),
        (ACTION_TYPE_ALL, ACTION_TYPE_ALL),
    ]

    SCOPE_CHOICES = [(SCOPE_TYPE_TASK, _("任务")), (SCOPE_TYPE_FLOW, _("流程")), (SCOPE_TYPE_ALL, _("全部"))]

    component_code = models.CharField(_("组件编码"), max_length=255)
    action = models.CharField(_("禁用动作"), max_length=32, choices=ACTION_CHOICES)
    scope = models.CharField(_("禁用范围"), max_length=32, choices=SCOPE_CHOICES)

    objects = DisabledComponentManager()

    class Meta:
        verbose_name = _("全局禁用的组件 DisabledComponent")
        verbose_name_plural = _("全局禁用的组件 DisabledComponent")
        index_together = ["scope", "action"]


class UserDefaultProjectManager(models.Manager):
    def init_user_default_project(self, username, project):
        try:
            return self.get(username=username)
        except UserDefaultProject.DoesNotExist:
            return self.create(username=username, default_project=project)


class UserDefaultProject(models.Model):
    username = models.CharField(_("用户名"), max_length=255, unique=True)
    default_project = models.ForeignKey(verbose_name=_("用户默认项目"), to=Project, on_delete=models.CASCADE)

    objects = UserDefaultProjectManager()

    class Meta:
        verbose_name = _("用户默认项目 UserDefaultProject")
        verbose_name_plural = _("用户默认项目 UserDefaultProject")

    def __unicode__(self):
        return "%s_%s" % (self.username, self.default_project)

    def __str__(self):
        return "%s_%s" % (self.username, self.default_project)


class ProjectCounterManager(models.Manager):
    def increase_or_create(self, username, project_id):
        obj = self.filter(username=username, project_id=project_id)
        if obj.exists():
            obj.update(count=models.F("count") + 1)
        else:
            self.create(username=username, project_id=project_id)


class ProjectCounter(models.Model):
    username = models.CharField(_("用户名"), max_length=255)
    project = models.ForeignKey(verbose_name=_("项目"), to=Project, on_delete=models.CASCADE)
    count = models.IntegerField(_("项目访问次数"), default=1)

    objects = ProjectCounterManager()

    class Meta:
        verbose_name = _("用户访问项目计数 ProjectCounter")
        verbose_name_plural = _("用户访问项目计数 ProjectCounter")

    def __unicode__(self):
        return "%s_%s_%s" % (self.username, self.project, self.count)

    def __str__(self):
        return "%s_%s_%s" % (self.username, self.project, self.count)


class ProjectConfigManager(models.Manager):
    def task_executor_for_project(self, project_id, executor):
        """获取项目下的任务执行者

        :param project_id: 项目 ID
        :type project_id: int
        :param executor: 当前任务执行者
        :type executor: str
        """
        qs = self.filter(project_id=project_id).values("executor_proxy", "executor_proxy_exempts")
        if not qs.exists():
            return executor

        executor_proxy = qs[0]["executor_proxy"].strip()
        executor_proxy_exempts = set(qs[0]["executor_proxy_exempts"].split(","))

        # 没有设置执行代理人，使用原执行人
        if not executor_proxy:
            return executor

        # 当前执行人在代理豁免人名单中，使用原执行人
        if executor in executor_proxy_exempts:
            return executor

        return executor_proxy


class StaffGroupSetManager(models.Manager):
    def get_members_with_group_ids(self, group_ids):
        return list(self.filter(id__in=group_ids, is_deleted=False).values_list("members", flat=True))


class StaffGroupSet(models.Model):
    """
    人员分组设置
    """

    project_id = models.IntegerField(_("项目 ID"))
    name = models.CharField(_("分组名称"), max_length=255)
    members = models.TextField(_("分组成员"), default="", help_text=_("多个成员以英文,分隔"), null=True, blank=True)
    is_deleted = models.BooleanField(_("是否已删除"), default=False)

    objects = StaffGroupSetManager()

    class Meta:
        verbose_name = _("人员分组设置 StaffGroupSet")
        verbose_name_plural = _("人员分组设置 StaffGroupSet")

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    def delete(self, real_delete=False):
        if real_delete:
            return super().delete()
        setattr(self, "is_deleted", True)
        self.save()


class ProjectConfig(models.Model):
    project_id = models.IntegerField(_("项目 ID"))
    executor_proxy = models.CharField(_("任务执行人代理"), max_length=255, default="", blank=True)
    executor_proxy_exempts = models.TextField(_("不使用执行人代理的用户列表"), default="", blank=True)
    max_periodic_task_num = models.IntegerField(_("项目下最大周期任务数"), default=-1, blank=True)

    objects = ProjectConfigManager()

    class Meta:
        verbose_name = _("项目配置 ProjectConfig")
        verbose_name_plural = _("项目配置 ProjectConfig")


class EngineConfigManager(models.Manager):
    def get_engine_ver(self, project_id, template_id, template_source):
        template_config = self.filter(
            scope_id=template_id, scope=EngineConfig.SCOPE_TYPE_TEMPLATE, template_source=template_source
        ).only("engine_ver")
        if template_config:
            return template_config.first().engine_ver

        project_config = self.filter(scope_id=project_id, scope=EngineConfig.SCOPE_TYPE_PROJECT).only("engine_ver")
        if project_config:
            return project_config.first().engine_ver

        return EngineConfig.ENGINE_VER_V2


class EngineConfig(models.Model):
    SCOPE_TYPE_PROJECT = 1
    SCOPE_TYPE_TEMPLATE = 2
    SCOPE_TYPE = ((SCOPE_TYPE_PROJECT, "project"), (SCOPE_TYPE_TEMPLATE, "template"))
    ENGINE_VER_V1 = 1
    ENGINE_VER_V2 = 2
    ENGINE_VER = ((ENGINE_VER_V1, "v1"), (ENGINE_VER_V2, "v2"))
    VALID_ENGINE_VER = {ENGINE_VER_V1, ENGINE_VER_V2}

    scope_id = models.IntegerField(_("范围对象ID"))
    scope = models.IntegerField(_("配置范围"), choices=SCOPE_TYPE)
    engine_ver = models.IntegerField(_("引擎版本"), choices=ENGINE_VER)
    template_source = models.CharField(_("流程模板来源"), max_length=32, choices=TEMPLATE_SOURCE)

    objects = EngineConfigManager()

    class Meta:
        verbose_name = _("引擎版本配置 EngineConfig")
        verbose_name_plural = _("引擎版本配置 EngineConfig")
        index_together = ["scope", "scope_id"]

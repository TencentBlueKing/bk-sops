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

from os import environ

from auth_backend.resources.base import resource_type_lib

from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import Group
from django.db import models, transaction
from django.utils import timezone


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

    groups = models.ManyToManyField(
        Group,
        through='BusinessGroupMembership'
    )

    objects = BusinessManager()

    # LifeCycle：'1'：测试中， '2'：已上线， '3'： 停运， 其他如'0'、''是历史遗留非法值，暂时认为是已上线状态
    LIFE_CYCLE_TESTING = '1'  # 测试中
    LIFE_CYCLE_ONLINE = '2'  # 已上线
    LIFE_CYCLE_CLOSE_DOWN = '3'  # 停运

    class Meta:
        verbose_name = _("业务 Business")
        verbose_name_plural = _("业务 Business")
        permissions = (
            ("view_business", "Can view business"),
            ("manage_business", "Can manage business"),
        )

    def __unicode__(self):
        return "%s_%s" % (self.cc_id, self.cc_name)

    def __str__(self):
        return "%s_%s" % (self.cc_id, self.cc_name)

    def available(self):
        return self.status != 'disabled'


class UserBusiness(models.Model):
    """
    用户默认业务表
    """
    user = models.CharField(_("用户QQ"), max_length=255, unique=True)
    default_buss = models.IntegerField(_("默认业务"))

    def __unicode__(self):
        return '%s_%s' % (self.user, self.default_buss)

    class Meta:
        verbose_name = _("用户默认业务 UserBusiness")
        verbose_name_plural = _("用户默认业务 UserBusiness")


class BusinessGroupMembership(models.Model):
    business = models.ForeignKey(Business)
    group = models.ForeignKey(Group)

    date_created = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = _("业务用户组 BusinessGroupMembership")
        verbose_name_plural = _("业务用户组 BusinessGroupMembership")
        unique_together = ('business', 'group')

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


class ProjectManager(models.Manager):

    def sync_project_from_cmdb_business(self, businesses):
        with transaction.atomic():
            if not businesses:
                return

            exist_sync_cc_id = set(self.filter(from_cmdb=True).values_list('bk_biz_id', flat=True))
            to_be_sync_cc_id = set(businesses.keys()) - exist_sync_cc_id
            projects = []

            # update exist business project
            exist_projects = self.all()
            for exist_project in exist_projects:
                business = businesses.get(exist_project.bk_biz_id)
                if not business:
                    continue

                if exist_project.name != business['cc_name']:
                    exist_project.name = business['cc_name']
                    exist_project.save()

            for cc_id in to_be_sync_cc_id:
                biz = businesses[cc_id]
                projects.append(Project(name=biz['cc_name'],
                                        time_zone=biz['time_zone'],
                                        creator=biz['creator'],
                                        desc='',
                                        from_cmdb=True,
                                        bk_biz_id=cc_id))

            self.bulk_create(projects, batch_size=5000)

            projects = Project.objects.filter(from_cmdb=True, bk_biz_id__in=to_be_sync_cc_id)

            if projects:
                project_resource = resource_type_lib['project']
                project_resource.batch_register_instance(list(projects))

    def update_business_project_status(self, archived_cc_ids, active_cc_ids):
        self.filter(bk_biz_id__in=archived_cc_ids, from_cmdb=True).update(is_disable=True)
        self.filter(bk_biz_id__in=active_cc_ids, from_cmdb=True).update(is_disable=False)


class Project(models.Model):
    name = models.CharField(_("项目名"), max_length=256)
    time_zone = models.CharField(_("项目时区"), max_length=100, blank=True)
    creator = models.CharField(_("创建者"), max_length=256)
    desc = models.CharField(_("项目描述"), max_length=512, blank=True)
    create_at = models.DateTimeField(_("创建时间"), auto_now_add=True)
    from_cmdb = models.BooleanField(_("是否是从 CMDB 业务同步过来的项目"), default=False)
    bk_biz_id = models.IntegerField(_("业务同步项目对应的 CMDB 业务 ID"), default=-1)
    is_disable = models.BooleanField(_("是否已停用"), default=False)
    relate_business = models.ManyToManyField(verbose_name=_("关联项目"), to=Business, blank=True)

    objects = ProjectManager()

    class Meta:
        verbose_name = _("项目 Project")
        verbose_name_plural = _("项目 Project")

    def __unicode__(self):
        return '%s_%s' % (self.id, self.name)

    def __str__(self):
        return '%s_%s' % (self.id, self.name)


class UserDefaultProjectManager(models.Manager):

    def init_user_default_project(self, username, project):
        try:
            return self.get(username=username)
        except UserDefaultProject.DoesNotExist:
            return self.create(username=username, default_project=project)


class UserDefaultProject(models.Model):
    username = models.CharField(_("用户名"), max_length=255, unique=True)
    default_project = models.ForeignKey(verbose_name=_("用户默认项目"), to=Project)

    objects = UserDefaultProjectManager()

    class Meta:
        verbose_name = _("用户默认项目 UserDefaultProject")
        verbose_name_plural = _("用户默认项目 UserDefaultProject")

    def __unicode__(self):
        return '%s_%s' % (self.username, self.default_project)

    def __str__(self):
        return '%s_%s' % (self.username, self.default_project)


class ProjectCounterManager(models.Manager):

    def increase_or_create(self, username, project_id):
        obj = self.filter(username=username, project_id=project_id)
        if obj.exists():
            obj.update(count=models.F('count') + 1)
        else:
            self.create(username=username, project_id=project_id)


class ProjectCounter(models.Model):
    username = models.CharField(_(u"用户名"), max_length=255)
    project = models.ForeignKey(verbose_name=_(u"项目"), to=Project)
    count = models.IntegerField(_(u"项目访问次数"), default=1)

    objects = ProjectCounterManager()

    class Meta:
        verbose_name = _(u"用户访问项目计数 ProjectCounter")
        verbose_name_plural = _(u"用户访问项目计数 ProjectCounter")

    def __unicode__(self):
        return '%s_%s_%s' % (self.username, self.project, self.count)

    def __str__(self):
        return '%s_%s_%s' % (self.username, self.project, self.count)

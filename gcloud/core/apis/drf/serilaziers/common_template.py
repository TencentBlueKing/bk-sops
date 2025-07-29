# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2022 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import json

from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from gcloud.common_template.models import CommonTemplate
from gcloud.constants import DATETIME_FORMAT, TASK_CATEGORY
from gcloud.core.apis.drf.serilaziers.template import BaseTemplateSerializer
from gcloud.constants import COMMON
from gcloud.core.models import Project


class CommonTemplateListSerializer(BaseTemplateSerializer):
    category_name = serializers.CharField(help_text="分类名称")
    create_time = serializers.DateTimeField(help_text="创建时间", format=DATETIME_FORMAT)
    creator_name = serializers.CharField(help_text="创建者名")
    description = serializers.CharField(help_text="公共流程描述", source="pipeline_template.description")
    editor_name = serializers.CharField(help_text="编辑者名称")
    edit_time = serializers.DateTimeField(help_text="编辑时间", format=DATETIME_FORMAT)
    has_subprocess = serializers.BooleanField(help_text="是否有子流程")
    name = serializers.CharField(help_text="公共流程名称")
    pipeline_template = serializers.IntegerField(help_text="pipeline模板ID", source="pipeline_template.id")
    subprocess_has_update = serializers.BooleanField(help_text="子流程是否更新")
    template_id = serializers.IntegerField(help_text="流程ID")
    subprocess_info = serializers.DictField(read_only=True, help_text="子流程信息")
    version = serializers.CharField(help_text="流程版本")
    project_scope = serializers.SerializerMethodField(help_text="流程使用范围")
    project_scope_name = serializers.SerializerMethodField(help_text="流程范围项目名称")

    class Meta:
        model = CommonTemplate
        exclude = ["extra_info"]

    def get_project_scope(self, obj):
        return obj.extra_info.get("project_scope")

    def get_project_scope_name(self, obj):
        project_scope = obj.extra_info.get("project_scope")
        if project_scope == ["*"]:
            return project_scope
        else:
            project_list = Project.objects.filter(id__in=project_scope).values_list("name", flat=True)
            return project_list


class CommonTemplateSerializer(CommonTemplateListSerializer):
    pipeline_tree = serializers.SerializerMethodField(read_only=True, help_text="pipeline_tree")

    def get_pipeline_tree(self, obj):
        return json.dumps(obj.pipeline_tree)


class TopCollectionCommonTemplateSerializer(CommonTemplateSerializer):
    is_collected = serializers.BooleanField(read_only=True, help_text="是否收藏")
    collection_id = serializers.IntegerField(read_only=True, help_text="收藏ID")


class CreateCommonTemplateSerializer(BaseTemplateSerializer):
    name = serializers.CharField(help_text="流程模板名称")
    category = serializers.ChoiceField(choices=TASK_CATEGORY, help_text="模板分类")
    time_out = serializers.IntegerField(help_text="超时时间", required=False)
    description = serializers.CharField(help_text="流程模板描述", allow_blank=True, required=False)
    pipeline_tree = serializers.CharField()
    id = serializers.IntegerField(help_text="公共流程ID", read_only=True)
    creator_name = serializers.CharField(read_only=True, help_text="创建者名")
    category_name = serializers.CharField(read_only=True, help_text="分类名称")
    editor_name = serializers.CharField(read_only=True, help_text="编辑者名")
    create_time = serializers.DateTimeField(read_only=True, help_text="创建时间", format=DATETIME_FORMAT)
    edit_time = serializers.DateTimeField(read_only=True, help_text="编辑时间", format=DATETIME_FORMAT)
    has_subprocess = serializers.BooleanField(read_only=True, help_text="是否有子流程")
    subprocess_has_update = serializers.BooleanField(help_text="子流程是否更新", read_only=True)
    template_id = serializers.IntegerField(help_text="流程ID", read_only=True)
    version = serializers.CharField(help_text="流程版本", read_only=True)
    pipeline_template = serializers.IntegerField(
        help_text="pipeline模板ID", source="pipeline_template.id", read_only=True
    )
    project_scope = serializers.ListSerializer(
        child=serializers.CharField(), help_text="流程使用范围", allow_empty=False, source="extra_info.project_scope"
    )

    def _calculate_new_executor_proxies(self, old_pipeline_tree: dict, pipeline_tree: dict):
        new_executor_proxies = set()
        old_nodes = old_pipeline_tree.get("activities", {})
        for node_id, node in pipeline_tree.get("activities", {}).items():
            executor_proxy = node.get("executor_proxy")
            if not executor_proxy:
                continue
            old_executor_proxy = old_nodes.get(node_id, {}).get("executor_proxy")
            if not old_executor_proxy or executor_proxy != old_executor_proxy:
                new_executor_proxies.add(executor_proxy)
        return new_executor_proxies

    def _calculate_executor_proxies(self, pipeline_tree):
        new_executor_proxies = set()
        for node_id, node in pipeline_tree.get("activities", {}).items():
            executor_proxy = node.get("executor_proxy")
            if not executor_proxy:
                continue
            new_executor_proxies.add(executor_proxy)
        return new_executor_proxies

    def validate_pipeline_tree(self, value: str):
        pipeline_tree = json.loads(value)
        old_pipeline_tree = self.instance.pipeline_tree if self.instance else None
        if old_pipeline_tree:
            # update
            new_executor_proxies = self._calculate_new_executor_proxies(old_pipeline_tree, pipeline_tree)
        else:
            # create
            new_executor_proxies = self._calculate_executor_proxies(pipeline_tree)
        user = getattr(self.context.get("request"), "user", None)
        if not user:
            raise serializers.ValidationError("user can not be empty.")
        if len(new_executor_proxies) > 1 or (new_executor_proxies and user.username != new_executor_proxies.pop()):
            raise serializers.ValidationError(_("代理人仅可设置为本人"))
        return value

    def _validate_scope_changes(self, scope_value):
        if scope_value == ["*"]:
            return

        references = self.instance.referencer()
        if not references:
            return

        scope_set = set(scope_value)
        conflict_projects = set()
        conflicts_project_templates = set()
        conflicts_common_templates = []
        for item in references:
            if item.get("template_type") != COMMON:
                project_id = str(item["project_id"])
                if project_id not in scope_value:
                    conflicts_project_templates.add(item["project_name"])
            else:
                item_scope = item.get("project_scope", [])
                if item_scope == ["*"]:
                    raise serializers.ValidationError(
                        f"当前流程与父流程 {item['name']} 的可见范围存在冲突，父流程允许所有项目可见，请遵循父流程的可见范围不能超出子流程的规则"
                    )

                if not set(item_scope).issubset(scope_set):
                    conflicting_projects = sorted(set(item_scope) - scope_set)
                    project_names = Project.objects.filter(id__in=conflicting_projects).values_list("name", flat=True)
                    conflicts_common_templates.append(item["name"])
                    conflict_projects.update(project_names)

        if conflicts_common_templates:
            err_message = (
                f"当前流程与父流程 {', '.join(conflicts_common_templates)} 的可见范围存在冲突，"
                f"请遵循父流程的可见范围不能超出子流程的规则，至少包含项目 {', '.join(sorted(conflict_projects))}"
            )
            raise serializers.ValidationError(err_message)

        if conflicts_project_templates:
            err_message = f"当前流程在项目 {', '.join(conflicts_project_templates)} 中被引用，请遵循流程可见范围限制"
            raise serializers.ValidationError(err_message)

    def _validate_child_scope(self, pipeline_tree, project_scope):
        project_scope_set = set(project_scope)
        conflict_details = set()
        subprocess = []
        for activity in pipeline_tree.get("activities", {}).values():
            if activity.get("type") != "SubProcess" or activity.get("template_source") != "common":
                continue
            common_template = CommonTemplate.objects.get(id=activity["template_id"])
            common_scope = common_template.extra_info.get("project_scope", [])
            if common_scope == ["*"]:
                continue
            if project_scope == ["*"] and common_scope != ["*"]:
                raise serializers.ValidationError(
                    f"当前流程与子流程 {common_template.pipeline_template.name} 的可见范围存在冲突，"
                    f"当前流程允许所有项目可见，请遵循父流程的可见范围不能超出子流程的规则"
                )
            if not project_scope_set.issubset(set(common_scope)):
                conflicting_projects = sorted(project_scope_set - set(common_scope))
                project_names = Project.objects.filter(id__in=conflicting_projects).values_list("name", flat=True)
                subprocess.append(common_template.pipeline_template.name)
                conflict_details.update(project_names)

        if subprocess:
            error_messages = (
                f"当前流程与子流程 {', '.join(subprocess)} 的可见范围存在冲突，"
                f"请遵循父流程的可见范围不能超出子流程的规则，需要移除项目 {', '.join(set(conflict_details))}"
            )
            raise serializers.ValidationError(error_messages)
        return pipeline_tree

    def validate(self, attrs):
        project_scope = attrs.get("extra_info").get("project_scope")
        request = self.context.get("request")
        # 检测其引用的子流程
        self._validate_child_scope(json.loads(attrs["pipeline_tree"]), project_scope)

        if request.method in ("PUT", "PATCH"):
            # 检测其被作为子流程引用的父流程
            self._validate_scope_changes(project_scope)

        return attrs

    class Meta:
        model = CommonTemplate
        fields = [
            "id",
            "name",
            "category",
            "time_out",
            "description",
            "notify_type",
            "notify_receivers",
            "pipeline_tree",
            "creator_name",
            "category_name",
            "editor_name",
            "create_time",
            "edit_time",
            "has_subprocess",
            "subprocess_has_update",
            "template_id",
            "version",
            "pipeline_template",
            "project_scope",
        ]


class PatchCommonTemplateSerializer(CreateCommonTemplateSerializer):
    class Meta:
        model = CommonTemplate
        fields = ["project_scope"]

    def validate(self, attrs):
        project_scope = attrs.get("extra_info").get("project_scope", [])
        self._validate_scope_changes(project_scope)
        self._validate_child_scope(self.instance.pipeline_tree, project_scope)
        return attrs

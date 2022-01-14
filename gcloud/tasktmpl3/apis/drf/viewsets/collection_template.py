# -*- coding: utf-8 -*-
import json
import logging

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.viewsets import GenericViewSet

from gcloud.contrib.collection.models import Collection
from gcloud.core.apis.drf.viewsets import ApiMixin
from gcloud.core.apis.drf.viewsets.utils import IAMMixin

from gcloud.iam_auth import get_iam_client, IAMMeta
from gcloud.iam_auth.resource_helpers.collection_template import CollectionTemplateResourceHelper
from gcloud.label.models import TemplateLabelRelation
from gcloud.tasktmpl3.apis.drf.filters import TaskTemplateFilter
from gcloud.tasktmpl3.apis.drf.permissions import CollectionTaskPermissions

from gcloud.tasktmpl3.apis.drf.serilaziers.collection_template import CollectionTemplateSerializer, ProjectSerializer
from gcloud.tasktmpl3.models import TaskTemplate

logger = logging.getLogger("root")
iam = get_iam_client()


class CollectionTemplateViewSet(ApiMixin, IAMMixin, GenericViewSet, generics.ListAPIView):
    queryset = TaskTemplate.objects.all()
    serializer_class = CollectionTemplateSerializer
    permission_classes = [permissions.IsAuthenticated, CollectionTaskPermissions]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = TaskTemplateFilter
    ordering_fields = ('id', 'edit_time')
    pagination_class = LimitOffsetPagination
    iam_resource_helper = CollectionTemplateResourceHelper(
        iam=iam,
        system=IAMMeta.SYSTEM_ID,
        actions=[
            IAMMeta.FLOW_VIEW_ACTION,
            IAMMeta.FLOW_EDIT_ACTION,
            IAMMeta.FLOW_DELETE_ACTION,
            IAMMeta.FLOW_CREATE_TASK_ACTION,
            IAMMeta.FLOW_CREATE_MINI_APP_ACTION,
            IAMMeta.FLOW_CREATE_PERIODIC_TASK_ACTION,
            IAMMeta.FLOW_CREATE_CLOCKED_TASK_ACTION,
        ],
    )

    def list(self, request, *args, **kwargs):
        user_collections = Collection.objects.filter(category="flow", username=request.user.username).values()
        project_id = int(request.query_params["project_id"])

        """
        collection_template_ids 筛选出用户在该项目收藏项目流程id列表
        collection_id_template_id_map 筛选出用户在该项目收藏项目流程id列表
        在一次循环中循环同时构建出收藏项目流程id列表和收藏id和模板id的映射
        构建出收藏id和模板id的映射是为了放进序列化器context中用于collection_id构建
        """
        collection_template_ids = []
        collection_id_template_id_map = {}
        for user_collection in user_collections:
            extra_info = json.loads(user_collection["extra_info"])
            if int(extra_info["project_id"]) == project_id:
                instance_id = user_collection["instance_id"]
                collection_template_ids.append(instance_id)
                collection_id_template_id_map[instance_id] = user_collection["id"]

        # 获得符合条件的模板
        current_project_collections = self.get_queryset().filter(id__in=collection_template_ids)
        filter_collections = self.filter_queryset(current_project_collections)

        # 取出当前页数
        current_page_collections = self.paginate_queryset(filter_collections)
        current_page_template_ids = [current_page_template.id for current_page_template in current_page_collections]

        # 获取labels上下文
        current_page_templates_labels = TemplateLabelRelation.objects.fetch_templates_labels(current_page_template_ids)

        # 获取auth_actions上下文
        template_auth_actions = self.iam_get_instances_auth_actions(request, list(current_page_collections))

        # 构建为序列化器注入的上下文
        serializer_context = {
            "collection_id_template_id_map": collection_id_template_id_map,
            "current_page_templates_labels": current_page_templates_labels,
            "template_auth_actions": template_auth_actions
        }

        # get_serializer_class是因为使用get_serializer的context会被默认的赋值,导致methodField访问不到上下文
        serializer = self.get_serializer_class()(current_page_collections, many=True, context=serializer_context)

        return self.get_paginated_response(serializer.data)

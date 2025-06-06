# -*- coding: utf-8 -*-
from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from gcloud.contrib.collection.models import Collection
from gcloud.contrib.collection.serializers import BatchCancelCollectionRequestSerializer, BatchCancelCollectionResponse
from gcloud.iam_auth.utils import check_project_or_admin_view_action_for_user


class BatchCancelCollectionApiView(APIView):
    @swagger_auto_schema(
        method="POST",
        operation_summary="批量取消收藏",
        request_body=BatchCancelCollectionRequestSerializer,
        responses={200: BatchCancelCollectionResponse},
    )
    @action(methods=["POST"], detail=False)
    def post(self, request):

        # 参数序列化校验
        serializer = BatchCancelCollectionRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer_data = serializer.data

        # 用户是否有该项目权限
        username = request.user.username
        project_id = serializer_data["project_id"]
        tenant_id = request.user.tenant_id
        if check_project_or_admin_view_action_for_user(project_id, username, tenant_id):
            return Response({"result": False, "message": "No permission in the current project"})

        # 用户在该项目下的收藏id列表
        collection_ids = Collection.objects.get_user_project_collection_category_ids(username, project_id, "flow")

        # 计算传来的收藏id与用户在该项目收藏id的差集
        batch_cancel_collection_ids = serializer_data["batch_cancel_collection_ids"]
        difference_ids = list(set(batch_cancel_collection_ids) - set(collection_ids))

        if difference_ids:
            return Response(
                {"result": False, "data": None, "message": "Does not exist collection id: {}".format(difference_ids)}
            )

        with transaction.atomic():
            Collection.objects.filter(id__in=batch_cancel_collection_ids).delete()
            return Response({"result": True, "data": None, "message": None})

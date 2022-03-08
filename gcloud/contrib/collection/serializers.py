# -*- coding: utf-8 -*-
from rest_framework import serializers


class BatchCancelCollectionRequestSerializer(serializers.Serializer):
    project_id = serializers.IntegerField(help_text="项目id")
    batch_cancel_collection_ids = serializers.ListSerializer(child=serializers.IntegerField(), help_text="批量取消的收藏id列表")


class BatchCancelCollectionResponse(serializers.Serializer):
    result = serializers.BooleanField(read_only=True, help_text="请求结果")
    data = serializers.JSONField(read_only=True, help_text="None")
    message = serializers.CharField(read_only=True, help_text="请求结果失败时返回信息")

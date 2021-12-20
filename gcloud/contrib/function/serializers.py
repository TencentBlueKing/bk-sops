# -*- coding: utf-8 -*-
from rest_framework import serializers


class FunctionTaskClaimantTransferRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text="职能化任务id")
    claimant = serializers.CharField(help_text="被转交人")


class FunctionTaskClaimantTransferResponse(serializers.Serializer):
    result = serializers.BooleanField(read_only=True, help_text="请求结果")
    message = serializers.CharField(read_only=True, help_text="请求结果失败时返回信息")

# -*- coding: utf-8 -*-
from bkapi_client_core.apigateway import APIGatewayClient, Operation, OperationGroup

class Group(OperationGroup):
    @property
    def add_related_apps(self) -> Operation:
        """
        bkapi resource add_related_apps
        添加网关关联应用
        """
    @property
    def apply_permissions(self) -> Operation:
        """
        bkapi resource apply_permissions
        申请网关API访问权限
        """
    @property
    def create_resource_version(self) -> Operation:
        """
        bkapi resource create_resource_version
        创建资源版本
        """
    @property
    def generate_sdk(self) -> Operation:
        """
        bkapi resource generate_sdk
        生成 SDK
        """
    @property
    def get_apigw_public_key(self) -> Operation:
        """
        bkapi resource get_apigw_public_key
        获取网关公钥
        """
    @property
    def get_apis(self) -> Operation:
        """
        bkapi resource get_apis
        查询网关
        """
    @property
    def get_latest_resource_version(self) -> Operation:
        """
        bkapi resource get_latest_resource_version
        获取网关最新版本
        """
    @property
    def get_released_resources(self) -> Operation:
        """
        bkapi resource get_released_resources
        查询已发布资源列表
        """
    @property
    def get_stages(self) -> Operation:
        """
        bkapi resource get_stages
        查询环境
        """
    @property
    def get_stages_with_resource_version(self) -> Operation:
        """
        bkapi resource get_stages_with_resource_version
        查询网关环境资源版本
        """
    @property
    def grant_permissions(self) -> Operation:
        """
        bkapi resource grant_permissions
        网关为应用主动授权
        """
    @property
    def import_resource_docs_by_archive(self) -> Operation:
        """
        bkapi resource import_resource_docs_by_archive
        通过文档归档文件导入资源文档
        """
    @property
    def import_resource_docs_by_swagger(self) -> Operation:
        """
        bkapi resource import_resource_docs_by_swagger
        通过 Swagger 格式导入文档
        """
    @property
    def list_resource_versions(self) -> Operation:
        """
        bkapi resource list_resource_versions
        """
    @property
    def release(self) -> Operation:
        """
        bkapi resource release
        发布版本
        """
    @property
    def revoke_permissions(self) -> Operation:
        """
        bkapi resource revoke_permissions
        回收应用访问网关 API 的权限
        """
    @property
    def sync_api(self) -> Operation:
        """
        bkapi resource sync_api
        同步网关
        """
    @property
    def sync_resources(self) -> Operation:
        """
        bkapi resource sync_resources
        同步资源
        """
    @property
    def sync_stage(self) -> Operation:
        """
        bkapi resource sync_stage
        同步环境
        """
    @property
    def update_gateway_status(self) -> Operation:
        """
        bkapi resource update_gateway_status
        修改网关状态
        """

class Client(APIGatewayClient):
    """Bkapi bk_apigateway client"""

    @property
    def api(self) -> Group:
        """api resources"""

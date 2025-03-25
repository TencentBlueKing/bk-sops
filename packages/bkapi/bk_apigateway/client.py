# -*- coding: utf-8 -*-
from bkapi_client_core.apigateway import APIGatewayClient, Operation, OperationGroup, bind_property


class Group(OperationGroup):
    # bkapi resource add_related_apps
    # 添加网关关联应用
    add_related_apps = bind_property(
        Operation,
        name="add_related_apps",
        method="POST",
        path="/api/v1/apis/{api_name}/related-apps/",
    )

    # bkapi resource apply_permissions
    # 申请网关API访问权限
    apply_permissions = bind_property(
        Operation,
        name="apply_permissions",
        method="POST",
        path="/api/v1/apis/{api_name}/permissions/apply/",
    )

    # bkapi resource create_resource_version
    # 创建资源版本
    create_resource_version = bind_property(
        Operation,
        name="create_resource_version",
        method="POST",
        path="/api/v1/apis/{api_name}/resource_versions/",
    )

    # bkapi resource generate_sdk
    # 生成 SDK
    generate_sdk = bind_property(
        Operation,
        name="generate_sdk",
        method="POST",
        path="/api/v1/apis/{api_name}/sdk/",
    )

    # bkapi resource get_apigw_public_key
    # 获取网关公钥
    get_apigw_public_key = bind_property(
        Operation,
        name="get_apigw_public_key",
        method="GET",
        path="/api/v1/apis/{api_name}/public_key/",
    )

    # bkapi resource get_apis
    # 查询网关
    get_apis = bind_property(
        Operation,
        name="get_apis",
        method="GET",
        path="/api/v1/apis/",
    )

    # bkapi resource get_latest_resource_version
    # 获取网关最新版本
    get_latest_resource_version = bind_property(
        Operation,
        name="get_latest_resource_version",
        method="GET",
        path="/api/v1/apis/{api_name}/resource_versions/latest/",
    )

    # bkapi resource get_released_resources
    # 查询已发布资源列表
    get_released_resources = bind_property(
        Operation,
        name="get_released_resources",
        method="GET",
        path="/api/v1/apis/{api_name}/released/stages/{stage_name}/resources/",
    )

    # bkapi resource get_stages
    # 查询环境
    get_stages = bind_property(
        Operation,
        name="get_stages",
        method="GET",
        path="/api/v1/apis/{api_name}/stages/",
    )

    # bkapi resource get_stages_with_resource_version
    # 查询网关环境资源版本
    get_stages_with_resource_version = bind_property(
        Operation,
        name="get_stages_with_resource_version",
        method="GET",
        path="/api/v1/apis/{api_name}/stages/with-resource-version/",
    )

    # bkapi resource grant_permissions
    # 网关为应用主动授权
    grant_permissions = bind_property(
        Operation,
        name="grant_permissions",
        method="POST",
        path="/api/v1/apis/{api_name}/permissions/grant/",
    )

    # bkapi resource import_resource_docs_by_archive
    # 通过文档归档文件导入资源文档
    import_resource_docs_by_archive = bind_property(
        Operation,
        name="import_resource_docs_by_archive",
        method="POST",
        path="/api/v1/apis/{api_name}/resource-docs/import/by-archive/",
    )

    # bkapi resource import_resource_docs_by_swagger
    # 通过 Swagger 格式导入文档
    import_resource_docs_by_swagger = bind_property(
        Operation,
        name="import_resource_docs_by_swagger",
        method="POST",
        path="/api/v1/apis/{api_name}/resource-docs/import/by-swagger/",
    )

    # bkapi resource list_resource_versions
    list_resource_versions = bind_property(
        Operation,
        name="list_resource_versions",
        method="GET",
        path="/api/v1/apis/{api_name}/resource_versions/",
    )

    # bkapi resource release
    # 发布版本
    release = bind_property(
        Operation,
        name="release",
        method="POST",
        path="/api/v1/apis/{api_name}/resource_versions/release/",
    )

    # bkapi resource revoke_permissions
    # 回收应用访问网关 API 的权限
    revoke_permissions = bind_property(
        Operation,
        name="revoke_permissions",
        method="DELETE",
        path="/api/v1/apis/{api_name}/permissions/revoke/",
    )

    # bkapi resource sync_api
    # 同步网关
    sync_api = bind_property(
        Operation,
        name="sync_api",
        method="POST",
        path="/api/v1/apis/{api_name}/sync/",
    )

    # bkapi resource sync_resources
    # 同步资源
    sync_resources = bind_property(
        Operation,
        name="sync_resources",
        method="POST",
        path="/api/v1/apis/{api_name}/resources/sync/",
    )

    # bkapi resource sync_stage
    # 同步环境
    sync_stage = bind_property(
        Operation,
        name="sync_stage",
        method="POST",
        path="/api/v1/apis/{api_name}/stages/sync/",
    )

    # bkapi resource update_gateway_status
    # 修改网关状态
    update_gateway_status = bind_property(
        Operation,
        name="update_gateway_status",
        method="POST",
        path="/api/v1/apis/{api_name}/status/",
    )


class Client(APIGatewayClient):
    """Bkapi bk_apigateway client"""

    _api_name = "bk-apigateway"

    api = bind_property(Group, name="api")

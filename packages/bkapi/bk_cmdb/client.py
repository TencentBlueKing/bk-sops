# -*- coding: utf-8 -*-
from bkapi_client_core.apigateway import APIGatewayClient, Operation, OperationGroup, bind_property


class Group(OperationGroup):
    # bkapi resource abort_transaction
    # AbortTransaction
    abort_transaction = bind_property(
        Operation,
        name="abort_transaction",
        method="POST",
        path="/api/v3/update/transaction/abort",
    )

    # bkapi resource add_cloud_host_to_biz
    # 新增云主机到业务的空闲机模块
    add_cloud_host_to_biz = bind_property(
        Operation,
        name="add_cloud_host_to_biz",
        method="POST",
        path="/api/v3/createmany/cloud_hosts",
    )

    # bkapi resource add_default_app
    # AddDefaultApp
    add_default_app = bind_property(
        Operation,
        name="add_default_app",
        method="POST",
        path="/api/v3/biz/default/{bk_supplier_account}",
    )

    # bkapi resource add_host_by_excel
    # AddHostByExcel
    add_host_by_excel = bind_property(
        Operation,
        name="add_host_by_excel",
        method="POST",
        path="/api/v3/hosts/excel/add",
    )

    # bkapi resource add_host_from_cmpy
    # 同步公司cmdb新增主机到cc3.0
    add_host_from_cmpy = bind_property(
        Operation,
        name="add_host_from_cmpy",
        method="POST",
        path="/api/v3/shipper/sync/cmdb/add_host_from_cmpy",
    )

    # bkapi resource add_host_lock
    # 新加主机锁
    add_host_lock = bind_property(
        Operation,
        name="add_host_lock",
        method="POST",
        path="/api/v3/host/lock",
    )

    # bkapi resource add_host_to_business_idle
    # 添加主机到业务空闲机
    add_host_to_business_idle = bind_property(
        Operation,
        name="add_host_to_business_idle",
        method="POST",
        path="/api/v3/hosts/add/business_idle",
    )

    # bkapi resource add_host_to_ci_biz
    # 将主机导入到“蓝盾测试机”业务下
    add_host_to_ci_biz = bind_property(
        Operation,
        name="add_host_to_ci_biz",
        method="POST",
        path="/api/v3/shipper/sync/cmdb/add_host_to_ci_biz",
    )

    # bkapi resource add_host_to_resource
    # 新增主机到资源池
    add_host_to_resource = bind_property(
        Operation,
        name="add_host_to_resource",
        method="POST",
        path="/api/v3/hosts/add",
    )

    # bkapi resource add_host_to_resource_pool
    # 添加主机到资源池
    add_host_to_resource_pool = bind_property(
        Operation,
        name="add_host_to_resource_pool",
        method="POST",
        path="/api/v3/hosts/add/resource",
    )

    # bkapi resource add_inst_by_import
    # AddInstByImport
    add_inst_by_import = bind_property(
        Operation,
        name="add_inst_by_import",
        method="POST",
        path="/api/v3/create/instance/object/{bk_obj_id}/by_import",
    )

    # bkapi resource add_instance_association
    # 新建模型实例之间的关联关系
    add_instance_association = bind_property(
        Operation,
        name="add_instance_association",
        method="POST",
        path="/api/v3/create/instassociation",
    )

    # bkapi resource add_label_for_service_instance
    # 为服务实例添加标签
    add_label_for_service_instance = bind_property(
        Operation,
        name="add_label_for_service_instance",
        method="POST",
        path="/api/v3/createmany/proc/service_instance/labels",
    )

    # bkapi resource add_object_batch
    # AddObjectBatch
    add_object_batch = bind_property(
        Operation,
        name="add_object_batch",
        method="POST",
        path="/api/v3/createmany/object",
    )

    # bkapi resource batch_create_inst
    # 批量创建通用模型实例
    batch_create_inst = bind_property(
        Operation,
        name="batch_create_inst",
        method="POST",
        path="/api/v3/createmany/instance/object/{bk_obj_id}",
    )

    # bkapi resource batch_create_instance_association
    # 批量创建模型实例关联关系
    batch_create_instance_association = bind_property(
        Operation,
        name="batch_create_instance_association",
        method="POST",
        path="/api/v3/createmany/instassociation",
    )

    # bkapi resource batch_create_kube_namespace
    # 批量创建namespace
    batch_create_kube_namespace = bind_property(
        Operation,
        name="batch_create_kube_namespace",
        method="POST",
        path="/api/v3/createmany/kube/namespace",
    )

    # bkapi resource batch_create_kube_node
    # 批量创建容器节点
    batch_create_kube_node = bind_property(
        Operation,
        name="batch_create_kube_node",
        method="POST",
        path="/api/v3/createmany/kube/node",
    )

    # bkapi resource batch_create_kube_pod
    # 批量创建容器pod
    batch_create_kube_pod = bind_property(
        Operation,
        name="batch_create_kube_pod",
        method="POST",
        path="/api/v3/createmany/kube/pod",
    )

    # bkapi resource batch_create_kube_workload
    # 批量创建workload
    batch_create_kube_workload = bind_property(
        Operation,
        name="batch_create_kube_workload",
        method="POST",
        path="/api/v3/createmany/kube/workload/{kind}",
    )

    # bkapi resource batch_create_module
    # 批量创建模块
    batch_create_module = bind_property(
        Operation,
        name="batch_create_module",
        method="POST",
        path="/api/v3/createmany/module",
    )

    # bkapi resource batch_create_proc_template
    # 批量创建进程模板
    batch_create_proc_template = bind_property(
        Operation,
        name="batch_create_proc_template",
        method="POST",
        path="/api/v3/createmany/proc/proc_template",
    )

    # bkapi resource batch_create_project
    # 批量创建项目
    batch_create_project = bind_property(
        Operation,
        name="batch_create_project",
        method="POST",
        path="/api/v3/createmany/project",
    )

    # bkapi resource batch_create_quoted_inst
    # 批量创建被引用的模型的实例
    batch_create_quoted_inst = bind_property(
        Operation,
        name="batch_create_quoted_inst",
        method="POST",
        path="/api/v3/createmany/quoted/instance",
    )

    # bkapi resource batch_delete_business_set
    # 批量删除业务集
    batch_delete_business_set = bind_property(
        Operation,
        name="batch_delete_business_set",
        method="POST",
        path="/api/v3/deletemany/biz_set",
    )

    # bkapi resource batch_delete_inst
    # 批量删除实例
    batch_delete_inst = bind_property(
        Operation,
        name="batch_delete_inst",
        method="DELETE",
        path="/api/v3/deletemany/instance/object/{bk_obj_id}",
    )

    # bkapi resource batch_delete_kube_cluster
    # 批量删除容器集群
    batch_delete_kube_cluster = bind_property(
        Operation,
        name="batch_delete_kube_cluster",
        method="DELETE",
        path="/api/v3/delete/kube/cluster",
    )

    # bkapi resource batch_delete_kube_namespace
    # 批量删除namespace
    batch_delete_kube_namespace = bind_property(
        Operation,
        name="batch_delete_kube_namespace",
        method="DELETE",
        path="/api/v3/deletemany/kube/namespace",
    )

    # bkapi resource batch_delete_kube_node
    # 批量删除容器节点
    batch_delete_kube_node = bind_property(
        Operation,
        name="batch_delete_kube_node",
        method="DELETE",
        path="/api/v3/deletemany/kube/node",
    )

    # bkapi resource batch_delete_kube_pod
    # 批量删除Pod
    batch_delete_kube_pod = bind_property(
        Operation,
        name="batch_delete_kube_pod",
        method="DELETE",
        path="/api/v3/deletemany/kube/pod",
    )

    # bkapi resource batch_delete_kube_workload
    # 批量删除workload
    batch_delete_kube_workload = bind_property(
        Operation,
        name="batch_delete_kube_workload",
        method="DELETE",
        path="/api/v3/deletemany/kube/workload/{kind}",
    )

    # bkapi resource batch_delete_project
    # 批量删除项目
    batch_delete_project = bind_property(
        Operation,
        name="batch_delete_project",
        method="DELETE",
        path="/api/v3/deletemany/project",
    )

    # bkapi resource batch_delete_quoted_inst
    # 批量删除被引用的模型的实例
    batch_delete_quoted_inst = bind_property(
        Operation,
        name="batch_delete_quoted_inst",
        method="DELETE",
        path="/api/v3/deletemany/quoted/instance",
    )

    # bkapi resource batch_delete_set
    # 批量删除集群
    batch_delete_set = bind_property(
        Operation,
        name="batch_delete_set",
        method="DELETE",
        path="/api/v3/set/{bk_biz_id}/batch",
    )

    # bkapi resource batch_update_business_set
    # 批量更新业务集信息
    batch_update_business_set = bind_property(
        Operation,
        name="batch_update_business_set",
        method="PUT",
        path="/api/v3/updatemany/biz_set",
    )

    # bkapi resource batch_update_host
    # 批量更新主机属性
    batch_update_host = bind_property(
        Operation,
        name="batch_update_host",
        method="PUT",
        path="/api/v3/hosts/property/batch",
    )

    # bkapi resource batch_update_host_all_properties
    # 根据主机id和属性批量更新主机属性
    batch_update_host_all_properties = bind_property(
        Operation,
        name="batch_update_host_all_properties",
        method="PUT",
        path="/api/v3/updatemany/hosts/all/property",
    )

    # bkapi resource batch_update_inst
    # 批量更新对象实例
    batch_update_inst = bind_property(
        Operation,
        name="batch_update_inst",
        method="PUT",
        path="/api/v3/updatemany/instance/object/{bk_obj_id}",
    )

    # bkapi resource batch_update_kube_cluster
    # 批量更新容器集群信息
    batch_update_kube_cluster = bind_property(
        Operation,
        name="batch_update_kube_cluster",
        method="PUT",
        path="/api/v3/updatemany/kube/cluster",
    )

    # bkapi resource batch_update_kube_namespace
    # 批量更新namespace
    batch_update_kube_namespace = bind_property(
        Operation,
        name="batch_update_kube_namespace",
        method="PUT",
        path="/api/v3/updatemany/kube/namespace",
    )

    # bkapi resource batch_update_kube_node
    # 批量更新容器节点信息
    batch_update_kube_node = bind_property(
        Operation,
        name="batch_update_kube_node",
        method="PUT",
        path="/api/v3/updatemany/kube/node",
    )

    # bkapi resource batch_update_kube_workload
    # 批量更新workload
    batch_update_kube_workload = bind_property(
        Operation,
        name="batch_update_kube_workload",
        method="PUT",
        path="/api/v3/updatemany/kube/workload/{kind}",
    )

    # bkapi resource batch_update_project
    # 批量更新项目
    batch_update_project = bind_property(
        Operation,
        name="batch_update_project",
        method="PUT",
        path="/api/v3/updatemany/project",
    )

    # bkapi resource batch_update_quoted_inst
    # 批量更新被引用的模型的实例
    batch_update_quoted_inst = bind_property(
        Operation,
        name="batch_update_quoted_inst",
        method="PUT",
        path="/api/v3/updatemany/quoted/instance",
    )

    # bkapi resource bind_host_agent
    # 将agent绑定到主机上
    bind_host_agent = bind_property(
        Operation,
        name="bind_host_agent",
        method="POST",
        path="/api/v3/host/bind/agent",
    )

    # bkapi resource check_objectattr_host_apply_enabled
    # check_objectattr_host_apply_enabled
    check_objectattr_host_apply_enabled = bind_property(
        Operation,
        name="check_objectattr_host_apply_enabled",
        method="POST",
        path="/api/v3/check/objectattr/host_apply_enabled",
    )

    # bkapi resource clone_host_property
    # 克隆主机属性
    clone_host_property = bind_property(
        Operation,
        name="clone_host_property",
        method="PUT",
        path="/api/v3/hosts/property/clone",
    )

    # bkapi resource clone_host_service_instance_proc
    # 克隆主机服务实例下的进程信息到新的主机服务实例中
    clone_host_service_instance_proc = bind_property(
        Operation,
        name="clone_host_service_instance_proc",
        method="POST",
        path="/api/v3/sidecar/update/clone/service/instance/process/biz/{bk_biz_id}",
    )

    # bkapi resource commit_transaction
    # CommitTransaction
    commit_transaction = bind_property(
        Operation,
        name="commit_transaction",
        method="POST",
        path="/api/v3/update/transaction/commit",
    )

    # bkapi resource count_biz_host_cpu
    # 统计每个业务下主机CPU数量（成本管理专用接口）
    count_biz_host_cpu = bind_property(
        Operation,
        name="count_biz_host_cpu",
        method="POST",
        path="/api/v3/host/count/cpu",
    )

    # bkapi resource count_instance_associations
    # 查询模型实例关系数量
    count_instance_associations = bind_property(
        Operation,
        name="count_instance_associations",
        method="POST",
        path="/api/v3/count/instance_associations/object/{bk_obj_id}",
    )

    # bkapi resource count_object_instances
    # 查询模型实例数量
    count_object_instances = bind_property(
        Operation,
        name="count_object_instances",
        method="POST",
        path="/api/v3/count/instances/object/{bk_obj_id}",
    )

    # bkapi resource count_object_instances_by_filters
    # count_object_instances_by_filters
    count_object_instances_by_filters = bind_property(
        Operation,
        name="count_object_instances_by_filters",
        method="POST",
        path="/api/v3/count/{bk_obj_id}/instances",
    )

    # bkapi resource create_biz_custom_field
    # 创建业务自定义模型属性
    create_biz_custom_field = bind_property(
        Operation,
        name="create_biz_custom_field",
        method="POST",
        path="/api/v3/create/objectattr/biz/{bk_biz_id}",
    )

    # bkapi resource create_business
    # 新建业务
    create_business = bind_property(
        Operation,
        name="create_business",
        method="POST",
        path="/api/v3/biz/{bk_supplier_account}",
    )

    # bkapi resource create_business_set
    # 创建业务集
    create_business_set = bind_property(
        Operation,
        name="create_business_set",
        method="POST",
        path="/api/v3/create/biz_set",
    )

    # bkapi resource create_classification
    # 添加模型分类
    create_classification = bind_property(
        Operation,
        name="create_classification",
        method="POST",
        path="/api/v3/create/objectclassification",
    )

    # bkapi resource create_cloud_area
    # 创建管控区域
    create_cloud_area = bind_property(
        Operation,
        name="create_cloud_area",
        method="POST",
        path="/api/v3/create/cloudarea",
    )

    # bkapi resource create_dynamic_group
    # 创建动态分组
    create_dynamic_group = bind_property(
        Operation,
        name="create_dynamic_group",
        method="POST",
        path="/api/v3/dynamicgroup",
    )

    # bkapi resource create_full_sync_cond_for_cache
    # 创建全量同步缓存条件
    create_full_sync_cond_for_cache = bind_property(
        Operation,
        name="create_full_sync_cond_for_cache",
        method="POST",
        path="/api/v3/cache/create/full/sync/cond",
    )

    # bkapi resource create_inst
    # 创建实例
    create_inst = bind_property(
        Operation,
        name="create_inst",
        method="POST",
        path="/api/v3/create/instance/object/{bk_obj_id}",
    )

    # bkapi resource create_kube_cluster
    # 创建容器集群
    create_kube_cluster = bind_property(
        Operation,
        name="create_kube_cluster",
        method="POST",
        path="/api/v3/create/kube/cluster",
    )

    # bkapi resource create_many_object
    # CreateManyObject
    create_many_object = bind_property(
        Operation,
        name="create_many_object",
        method="POST",
        path="/api/v3/createmany/object/by_import",
    )

    # bkapi resource create_module
    # 创建模块
    create_module = bind_property(
        Operation,
        name="create_module",
        method="POST",
        path="/api/v3/module/{bk_biz_id}/{bk_set_id}",
    )

    # bkapi resource create_object
    # 创建模型
    create_object = bind_property(
        Operation,
        name="create_object",
        method="POST",
        path="/api/v3/create/object",
    )

    # bkapi resource create_object_attribute
    # 创建模型属性
    create_object_attribute = bind_property(
        Operation,
        name="create_object_attribute",
        method="POST",
        path="/api/v3/create/objectattr",
    )

    # bkapi resource create_process_instance
    # 创建进程实例
    create_process_instance = bind_property(
        Operation,
        name="create_process_instance",
        method="POST",
        path="/api/v3/create/proc/process_instance",
    )

    # bkapi resource create_service_category
    # 新建服务分类
    create_service_category = bind_property(
        Operation,
        name="create_service_category",
        method="POST",
        path="/api/v3/create/proc/service_category",
    )

    # bkapi resource create_service_instance
    # 创建服务实例
    create_service_instance = bind_property(
        Operation,
        name="create_service_instance",
        method="POST",
        path="/api/v3/create/proc/service_instance",
    )

    # bkapi resource create_service_template
    # 新建服务模板
    create_service_template = bind_property(
        Operation,
        name="create_service_template",
        method="POST",
        path="/api/v3/create/proc/service_template",
    )

    # bkapi resource create_set
    # 创建集群
    create_set = bind_property(
        Operation,
        name="create_set",
        method="POST",
        path="/api/v3/set/{bk_biz_id}",
    )

    # bkapi resource create_set_template
    # 新建集群模板
    create_set_template = bind_property(
        Operation,
        name="create_set_template",
        method="POST",
        path="/api/v3/create/topo/set_template/bk_biz_id/{bk_biz_id}",
    )

    # bkapi resource delete_biz
    # DeleteBiz
    delete_biz = bind_property(
        Operation,
        name="delete_biz",
        method="POST",
        path="/api/v3/deletemany/biz",
    )

    # bkapi resource delete_classification
    # 删除模型分类
    delete_classification = bind_property(
        Operation,
        name="delete_classification",
        method="DELETE",
        path="/api/v3/delete/objectclassification/{id}",
    )

    # bkapi resource delete_cloud_area
    # 删除管控区域
    delete_cloud_area = bind_property(
        Operation,
        name="delete_cloud_area",
        method="DELETE",
        path="/api/v3/delete/cloudarea/{bk_cloud_id}",
    )

    # bkapi resource delete_cloud_host_from_biz
    # 从业务空闲机集群删除云主机
    delete_cloud_host_from_biz = bind_property(
        Operation,
        name="delete_cloud_host_from_biz",
        method="DELETE",
        path="/api/v3/deletemany/cloud_hosts",
    )

    # bkapi resource delete_delete_associationtype
    # delete_delete_associationtype
    delete_delete_associationtype = bind_property(
        Operation,
        name="delete_delete_associationtype",
        method="DELETE",
        path="/api/v3/delete/associationtype/{id}",
    )

    # bkapi resource delete_delete_cloud_account
    # delete_delete_cloud_account
    delete_delete_cloud_account = bind_property(
        Operation,
        name="delete_delete_cloud_account",
        method="DELETE",
        path="/api/v3/delete/cloud/account/{id}",
    )

    # bkapi resource delete_delete_cloud_sync_task
    # delete_delete_cloud_sync_task
    delete_delete_cloud_sync_task = bind_property(
        Operation,
        name="delete_delete_cloud_sync_task",
        method="DELETE",
        path="/api/v3/delete/cloud/sync/task/{id}",
    )

    # bkapi resource delete_delete_field_template
    # delete_delete_field_template
    delete_delete_field_template = bind_property(
        Operation,
        name="delete_delete_field_template",
        method="DELETE",
        path="/api/v3/delete/field_template",
    )

    # bkapi resource delete_delete_objectassociation
    # delete_delete_objectassociation
    delete_delete_objectassociation = bind_property(
        Operation,
        name="delete_delete_objectassociation",
        method="DELETE",
        path="/api/v3/delete/objectassociation/{id}",
    )

    # bkapi resource delete_delete_objectattgroup
    # delete_delete_objectattgroup
    delete_delete_objectattgroup = bind_property(
        Operation,
        name="delete_delete_objectattgroup",
        method="DELETE",
        path="/api/v3/delete/objectattgroup/{id}",
    )

    # bkapi resource delete_delete_operation_chart
    # delete_delete_operation_chart
    delete_delete_operation_chart = bind_property(
        Operation,
        name="delete_delete_operation_chart",
        method="DELETE",
        path="/api/v3/delete/operation/chart/{id}",
    )

    # bkapi resource delete_delete_proc_service_template_attribute
    # delete_delete_proc_service_template_attribute
    delete_delete_proc_service_template_attribute = bind_property(
        Operation,
        name="delete_delete_proc_service_template_attribute",
        method="DELETE",
        path="/api/v3/delete/proc/service_template/attribute",
    )

    # bkapi resource delete_delete_resource_directory
    # delete_delete_resource_directory
    delete_delete_resource_directory = bind_property(
        Operation,
        name="delete_delete_resource_directory",
        method="DELETE",
        path="/api/v3/delete/resource/directory/{id}",
    )

    # bkapi resource delete_delete_topo_set_template_attribute
    # delete_delete_topo_set_template_attribute
    delete_delete_topo_set_template_attribute = bind_property(
        Operation,
        name="delete_delete_topo_set_template_attribute",
        method="DELETE",
        path="/api/v3/delete/topo/set_template/attribute",
    )

    # bkapi resource delete_delete_topomodelmainline_object
    # delete_delete_topomodelmainline_object
    delete_delete_topomodelmainline_object = bind_property(
        Operation,
        name="delete_delete_topomodelmainline_object",
        method="DELETE",
        path="/api/v3/delete/topomodelmainline/object/{bk_obj_id}",
    )

    # bkapi resource delete_deletemany_proc_service_template_host_apply_rule_biz
    # delete_deletemany_proc_service_template_host_apply_rule_biz
    delete_deletemany_proc_service_template_host_apply_rule_biz = bind_property(
        Operation,
        name="delete_deletemany_proc_service_template_host_apply_rule_biz",
        method="DELETE",
        path="/api/v3/deletemany/proc/service_template/host_apply_rule/biz/{bk_biz_id}",
    )

    # bkapi resource delete_dynamic_group
    # 删除动态分组
    delete_dynamic_group = bind_property(
        Operation,
        name="delete_dynamic_group",
        method="DELETE",
        path="/api/v3/dynamicgroup/{bk_biz_id}/{id}",
    )

    # bkapi resource delete_full_sync_cond_for_cache
    # 删除全量同步缓存条件
    delete_full_sync_cond_for_cache = bind_property(
        Operation,
        name="delete_full_sync_cond_for_cache",
        method="DELETE",
        path="/api/v3/cache/delete/full/sync/cond",
    )

    # bkapi resource delete_host
    # 删除主机
    delete_host = bind_property(
        Operation,
        name="delete_host",
        method="DELETE",
        path="/api/v3/hosts/batch",
    )

    # bkapi resource delete_host_deletemany_module_host_apply_rule_bk_biz_id
    # delete_host_deletemany_module_host_apply_rule_bk_biz_id
    delete_host_deletemany_module_host_apply_rule_bk_biz_id = bind_property(
        Operation,
        name="delete_host_deletemany_module_host_apply_rule_bk_biz_id",
        method="DELETE",
        path="/api/v3/host/deletemany/module/host_apply_rule/bk_biz_id/{bk_biz_id}",
    )

    # bkapi resource delete_host_from_ci_biz
    # 删除(移出)“蓝盾测试机”业务下的主机
    delete_host_from_ci_biz = bind_property(
        Operation,
        name="delete_host_from_ci_biz",
        method="DELETE",
        path="/api/v3/shipper/delete/cmdb/delete_host_from_ci_biz",
    )

    # bkapi resource delete_host_lock
    # 删除主机锁
    delete_host_lock = bind_property(
        Operation,
        name="delete_host_lock",
        method="DELETE",
        path="/api/v3/host/lock",
    )

    # bkapi resource delete_hosts_favorites
    # delete_hosts_favorites
    delete_hosts_favorites = bind_property(
        Operation,
        name="delete_hosts_favorites",
        method="DELETE",
        path="/api/v3/hosts/favorites/{id}",
    )

    # bkapi resource delete_inst
    # 删除实例
    delete_inst = bind_property(
        Operation,
        name="delete_inst",
        method="DELETE",
        path="/api/v3/delete/instance/object/{bk_obj_id}/inst/{bk_inst_id}",
    )

    # bkapi resource delete_instance_association
    # 删除模型实例之间的关联关系
    delete_instance_association = bind_property(
        Operation,
        name="delete_instance_association",
        method="DELETE",
        path="/api/v3/delete/instassociation/{bk_obj_id}/{id}",
    )

    # bkapi resource delete_module
    # 删除模块
    delete_module = bind_property(
        Operation,
        name="delete_module",
        method="DELETE",
        path="/api/v3/module/{bk_biz_id}/{bk_set_id}/{bk_module_id}",
    )

    # bkapi resource delete_object
    # 删除模型
    delete_object = bind_property(
        Operation,
        name="delete_object",
        method="DELETE",
        path="/api/v3/delete/object/{id}",
    )

    # bkapi resource delete_object_attribute
    # 删除对象模型属性
    delete_object_attribute = bind_property(
        Operation,
        name="delete_object_attribute",
        method="DELETE",
        path="/api/v3/delete/objectattr/{id}",
    )

    # bkapi resource delete_proc_template
    # 删除进程模板
    delete_proc_template = bind_property(
        Operation,
        name="delete_proc_template",
        method="DELETE",
        path="/api/v3/deletemany/proc/proc_template",
    )

    # bkapi resource delete_process_instance
    # 删除进程实例
    delete_process_instance = bind_property(
        Operation,
        name="delete_process_instance",
        method="DELETE",
        path="/api/v3/delete/proc/process_instance",
    )

    # bkapi resource delete_related_inst_asso
    # 删除某实例所有的关联关系（包含其作为关联关系原模型和关联关系目标模型的情况）
    delete_related_inst_asso = bind_property(
        Operation,
        name="delete_related_inst_asso",
        method="DELETE",
        path="/api/v3/delete/instassociation/batch",
    )

    # bkapi resource delete_service_category
    # 删除服务分类
    delete_service_category = bind_property(
        Operation,
        name="delete_service_category",
        method="DELETE",
        path="/api/v3/delete/proc/service_category",
    )

    # bkapi resource delete_service_instance
    # 删除服务实例
    delete_service_instance = bind_property(
        Operation,
        name="delete_service_instance",
        method="DELETE",
        path="/api/v3/deletemany/proc/service_instance",
    )

    # bkapi resource delete_service_template
    # 删除服务模板
    delete_service_template = bind_property(
        Operation,
        name="delete_service_template",
        method="DELETE",
        path="/api/v3/delete/proc/service_template",
    )

    # bkapi resource delete_set
    # 删除集群
    delete_set = bind_property(
        Operation,
        name="delete_set",
        method="DELETE",
        path="/api/v3/set/{bk_biz_id}/{bk_set_id}",
    )

    # bkapi resource delete_set_template
    # 删除集群模板
    delete_set_template = bind_property(
        Operation,
        name="delete_set_template",
        method="DELETE",
        path="/api/v3/deletemany/topo/set_template/bk_biz_id/{bk_biz_id}",
    )

    # bkapi resource execute_dynamic_group
    # 执行动态分组
    execute_dynamic_group = bind_property(
        Operation,
        name="execute_dynamic_group",
        method="POST",
        path="/api/v3/dynamicgroup/data/{bk_biz_id}/{id}",
    )

    # bkapi resource find_association_by_object_association_i_d
    # FindAssociationByObjectAssociationID
    find_association_by_object_association_i_d = bind_property(
        Operation,
        name="find_association_by_object_association_i_d",
        method="POST",
        path="/api/v3/topo/find/object/{bk_obj_id}/association/by/bk_obj_asst_id",
    )

    # bkapi resource find_audit_by_id
    # 根据审计ID获取详细信息
    find_audit_by_id = bind_property(
        Operation,
        name="find_audit_by_id",
        method="POST",
        path="/api/v3/find/audit",
    )

    # bkapi resource find_biz_sensitive_batch
    # 批量查询业务敏感信息
    find_biz_sensitive_batch = bind_property(
        Operation,
        name="find_biz_sensitive_batch",
        method="POST",
        path="/api/v3/sidecar/findmany/sensitive/biz",
    )

    # bkapi resource find_biz_tree_brief_info
    # 查询业务topo树的简要信息, 只包含集群、模块和主机
    find_biz_tree_brief_info = bind_property(
        Operation,
        name="find_biz_tree_brief_info",
        method="POST",
        path="/api/v3/find/topo/tree/brief/biz/{bk_biz_id}",
    )

    # bkapi resource find_brief_biz_topo_node_relation
    # 查询业务主线实例拓扑源与目标节点的关系信息
    find_brief_biz_topo_node_relation = bind_property(
        Operation,
        name="find_brief_biz_topo_node_relation",
        method="POST",
        path="/api/v3/find/topo/biz/brief_node_relation",
    )

    # bkapi resource find_host_biz_relations
    # 查询主机业务关系信息
    find_host_biz_relations = bind_property(
        Operation,
        name="find_host_biz_relations",
        method="POST",
        path="/api/v3/hosts/modules/read",
    )

    # bkapi resource find_host_by_service_template
    # 查询服务模板下的主机
    find_host_by_service_template = bind_property(
        Operation,
        name="find_host_by_service_template",
        method="POST",
        path="/api/v3/findmany/hosts/by_service_templates/biz/{bk_biz_id}",
    )

    # bkapi resource find_host_by_set_template
    # 查询集群模板下的主机
    find_host_by_set_template = bind_property(
        Operation,
        name="find_host_by_set_template",
        method="POST",
        path="/api/v3/findmany/hosts/by_set_templates/biz/{bk_biz_id}",
    )

    # bkapi resource find_host_by_topo
    # 查询拓扑节点下的主机
    find_host_by_topo = bind_property(
        Operation,
        name="find_host_by_topo",
        method="POST",
        path="/api/v3/findmany/hosts/by_topo/biz/{bk_biz_id}",
    )

    # bkapi resource find_host_identifier_push_result
    # 获取推送主机身份任务结果
    find_host_identifier_push_result = bind_property(
        Operation,
        name="find_host_identifier_push_result",
        method="POST",
        path="/api/v3/event/find/host_identifier_push_result",
    )

    # bkapi resource find_host_relations_with_topo
    # 根据业务拓扑中的实例节点查询其下的主机关系信息
    find_host_relations_with_topo = bind_property(
        Operation,
        name="find_host_relations_with_topo",
        method="POST",
        path="/api/v3/findmany/hosts/relation/with_topo",
    )

    # bkapi resource find_host_topo_relation
    # 获取主机与拓扑的关系
    find_host_topo_relation = bind_property(
        Operation,
        name="find_host_topo_relation",
        method="POST",
        path="/api/v3/host/topo/relation/read",
    )

    # bkapi resource find_host_typeclass_relation
    # 查询公司cmdb服务器设备型号和类型对应关系
    find_host_typeclass_relation = bind_property(
        Operation,
        name="find_host_typeclass_relation",
        method="POST",
        path="/api/v3/sidecar/host/list_host_type_class_relation",
    )

    # bkapi resource find_inst_id_rule_task_status
    # 查询同步实例id规则字段状态
    find_inst_id_rule_task_status = bind_property(
        Operation,
        name="find_inst_id_rule_task_status",
        method="POST",
        path="/api/v3/find/inst/id_rule/task_status",
    )

    # bkapi resource find_instance_association
    # 查询模型实例之间的关联关系
    find_instance_association = bind_property(
        Operation,
        name="find_instance_association",
        method="POST",
        path="/api/v3/find/instassociation",
    )

    # bkapi resource find_instassociation_with_inst
    # 查询模型实例的关联关系及可选返回原模型或目标模型的实例详情
    find_instassociation_with_inst = bind_property(
        Operation,
        name="find_instassociation_with_inst",
        method="POST",
        path="/api/v3/find/instassociation/object/{bk_obj_id}/inst/detail",
    )

    # bkapi resource find_module_batch
    # 批量查询某业务的模块详情
    find_module_batch = bind_property(
        Operation,
        name="find_module_batch",
        method="POST",
        path="/api/v3/findmany/module/bk_biz_id/{bk_biz_id}",
    )

    # bkapi resource find_module_host_relation
    # 根据模块ID查询主机和模块的关系
    find_module_host_relation = bind_property(
        Operation,
        name="find_module_host_relation",
        method="POST",
        path="/api/v3/findmany/module_relation/bk_biz_id/{bk_biz_id}",
    )

    # bkapi resource find_module_with_relation
    # 根据条件查询业务下的模块
    find_module_with_relation = bind_property(
        Operation,
        name="find_module_with_relation",
        method="POST",
        path="/api/v3/findmany/module/with_relation/biz/{bk_biz_id}",
    )

    # bkapi resource find_object_association
    # 查询模型之间的关联关系
    find_object_association = bind_property(
        Operation,
        name="find_object_association",
        method="POST",
        path="/api/v3/find/objectassociation",
    )

    # bkapi resource find_set_batch
    # 批量查询某业务的集群详情
    find_set_batch = bind_property(
        Operation,
        name="find_set_batch",
        method="POST",
        path="/api/v3/findmany/set/bk_biz_id/{bk_biz_id}",
    )

    # bkapi resource find_topo_node_paths
    # 查询业务拓扑节点的拓扑路径
    find_topo_node_paths = bind_property(
        Operation,
        name="find_topo_node_paths",
        method="POST",
        path="/api/v3/cache/find/cache/topo/node_path/biz/{bk_biz_id}",
    )

    # bkapi resource get_biz_brief_cache_topo
    # 查询业务的简要拓扑树信息，包含所有层级的数据，不包含主机
    get_biz_brief_cache_topo = bind_property(
        Operation,
        name="get_biz_brief_cache_topo",
        method="GET",
        path="/api/v3/cache/find/cache/topo/brief/biz/{bk_biz_id}",
    )

    # bkapi resource get_biz_internal_module
    # 查询业务的空闲机/故障机/待回收模块
    get_biz_internal_module = bind_property(
        Operation,
        name="get_biz_internal_module",
        method="GET",
        path="/api/v3/topo/internal/{bk_supplier_account}/{bk_biz_id}",
    )

    # bkapi resource get_biz_kube_cache_topo
    # 查询业务的容器拓扑树缓存信息，包含业务、Cluster、Namespace、Workload层级的数据
    get_biz_kube_cache_topo = bind_property(
        Operation,
        name="get_biz_kube_cache_topo",
        method="POST",
        path="/api/v3/cache/find/biz/kube/topo",
    )

    # bkapi resource get_biz_location
    # 查询业务在cc1.0还是在cc3.0
    get_biz_location = bind_property(
        Operation,
        name="get_biz_location",
        method="POST",
        path="/api/v3/sidecar/get_biz_location",
    )

    # bkapi resource get_biz_simplify
    # get_biz_simplify
    get_biz_simplify = bind_property(
        Operation,
        name="get_biz_simplify",
        method="GET",
        path="/api/v3/biz/simplify",
    )

    # bkapi resource get_biz_with_reduced
    # get_biz_with_reduced
    get_biz_with_reduced = bind_property(
        Operation,
        name="get_biz_with_reduced",
        method="GET",
        path="/api/v3/biz/with_reduced",
    )

    # bkapi resource get_dynamic_group
    # 查询指定动态分组
    get_dynamic_group = bind_property(
        Operation,
        name="get_dynamic_group",
        method="GET",
        path="/api/v3/dynamicgroup/{bk_biz_id}/{id}",
    )

    # bkapi resource get_find_audit_dict
    # get_find_audit_dict
    get_find_audit_dict = bind_property(
        Operation,
        name="get_find_audit_dict",
        method="GET",
        path="/api/v3/find/audit_dict",
    )

    # bkapi resource get_find_field_template
    # get_find_field_template
    get_find_field_template = bind_property(
        Operation,
        name="get_find_field_template",
        method="GET",
        path="/api/v3/find/field_template/{id}",
    )

    # bkapi resource get_find_kube__attributes
    # get_find_kube__attributes
    get_find_kube__attributes = bind_property(
        Operation,
        name="get_find_kube__attributes",
        method="GET",
        path="/api/v3/find/kube/{bk_obj_id}/attributes",
    )

    # bkapi resource get_find_proc_service_template__detail
    # get_find_proc_service_template__detail
    get_find_proc_service_template__detail = bind_property(
        Operation,
        name="get_find_proc_service_template__detail",
        method="GET",
        path="/api/v3/find/proc/service_template/{id}/detail",
    )

    # bkapi resource get_find_topo_set_template__bk_biz_id
    # get_find_topo_set_template__bk_biz_id
    get_find_topo_set_template__bk_biz_id = bind_property(
        Operation,
        name="get_find_topo_set_template__bk_biz_id",
        method="GET",
        path="/api/v3/find/topo/set_template/{set_template_id}/bk_biz_id/{bk_biz_id}",
    )

    # bkapi resource get_findmany_biz_set_simplify
    # get_findmany_biz_set_simplify
    get_findmany_biz_set_simplify = bind_property(
        Operation,
        name="get_findmany_biz_set_simplify",
        method="GET",
        path="/api/v3/findmany/biz_set/simplify",
    )

    # bkapi resource get_findmany_biz_set_with_reduced
    # get_findmany_biz_set_with_reduced
    get_findmany_biz_set_with_reduced = bind_property(
        Operation,
        name="get_findmany_biz_set_with_reduced",
        method="GET",
        path="/api/v3/findmany/biz_set/with_reduced",
    )

    # bkapi resource get_findmany_operation_chart
    # get_findmany_operation_chart
    get_findmany_operation_chart = bind_property(
        Operation,
        name="get_findmany_operation_chart",
        method="GET",
        path="/api/v3/findmany/operation/chart",
    )

    # bkapi resource get_host_base_info
    # 获取主机详情
    get_host_base_info = bind_property(
        Operation,
        name="get_host_base_info",
        method="GET",
        path="/api/v3/hosts/{bk_supplier_account}/{bk_host_id}",
    )

    # bkapi resource get_host_data
    # GetHostData
    get_host_data = bind_property(
        Operation,
        name="get_host_data",
        method="POST",
        path="/api/v3/hosts/search/asstdetail",
    )

    # bkapi resource get_host_location
    # 根据主机IP及云区域ID查询该主机所属业务是在cc1.0还是在cc3.0
    get_host_location = bind_property(
        Operation,
        name="get_host_location",
        method="POST",
        path="/api/v3/sidecar/get_host_location",
    )

    # bkapi resource get_inst_detail
    # GetInstDetail
    get_inst_detail = bind_property(
        Operation,
        name="get_inst_detail",
        method="POST",
        path="/api/v3/find/instance/object/{bk_obj_id}",
    )

    # bkapi resource get_inst_unique_fields
    # GetInstUniqueFields
    get_inst_unique_fields = bind_property(
        Operation,
        name="get_inst_unique_fields",
        method="POST",
        path="/api/v3/find/instance/object/{bk_obj_id}/unique_fields/by/unique/{id}",
    )

    # bkapi resource get_mainline_object_topo
    # 查询主线模型的业务拓扑
    get_mainline_object_topo = bind_property(
        Operation,
        name="get_mainline_object_topo",
        method="POST",
        path="/api/v3/find/topomodelmainline",
    )

    # bkapi resource get_object_attr_with_table
    # GetObjectAttrWithTable
    get_object_attr_with_table = bind_property(
        Operation,
        name="get_object_attr_with_table",
        method="POST",
        path="/api/v3/find/objectattr/web",
    )

    # bkapi resource get_object_data
    # GetObjectData
    get_object_data = bind_property(
        Operation,
        name="get_object_data",
        method="POST",
        path="/api/v3/findmany/object",
    )

    # bkapi resource get_object_group
    # GetObjectGroup
    get_object_group = bind_property(
        Operation,
        name="get_object_group",
        method="POST",
        path="/api/v3/find/objectattgroup/object/{bk_obj_id}",
    )

    # bkapi resource get_proc_template
    # 获取进程模板
    get_proc_template = bind_property(
        Operation,
        name="get_proc_template",
        method="POST",
        path="/api/v3/find/proc/proc_template/id/{process_template_id}",
    )

    # bkapi resource get_service_template
    # 获取服务模板
    get_service_template = bind_property(
        Operation,
        name="get_service_template",
        method="GET",
        path="/api/v3/find/proc/service_template/{service_template_id}",
    )

    # bkapi resource get_topo_internal___with_statistics
    # get_topo_internal___with_statistics
    get_topo_internal___with_statistics = bind_property(
        Operation,
        name="get_topo_internal___with_statistics",
        method="GET",
        path="/api/v3/topo/internal/{bk_supplier_account}/{bk_biz_id}/with_statistics",
    )

    # bkapi resource group_related_resource_by_ids
    # group_related_resource_by_ids
    group_related_resource_by_ids = bind_property(
        Operation,
        name="group_related_resource_by_ids",
        method="POST",
        path="/api/v3/group/related/{kind}/resource/by_ids",
    )

    # bkapi resource health_check
    # HealthCheck
    health_check = bind_property(
        Operation,
        name="health_check",
        method="POST",
        path="/healthz",
    )

    # bkapi resource host_install_bk
    # 机器新加到蓝鲸业务拓扑中
    host_install_bk = bind_property(
        Operation,
        name="host_install_bk",
        method="POST",
        path="/api/v3/host/install/bk",
    )

    # bkapi resource hosts_cr_transit_to_idle
    # 将主机从业务的资源中转模块转移到空闲机模块
    hosts_cr_transit_to_idle = bind_property(
        Operation,
        name="hosts_cr_transit_to_idle",
        method="POST",
        path="/api/v3/shipper/transfer/cmdb/hosts_cr_transit_to_idle",
    )

    # bkapi resource hosts_to_cr_transit
    # 将主机转移到指定业务的资源中转模块
    hosts_to_cr_transit = bind_property(
        Operation,
        name="hosts_to_cr_transit",
        method="POST",
        path="/api/v3/shipper/transfer/cmdb/hosts_to_cr_transit",
    )

    # bkapi resource import_association
    # ImportAssociation
    import_association = bind_property(
        Operation,
        name="import_association",
        method="POST",
        path="/api/v3/import/instassociation/{bk_obj_id}",
    )

    # bkapi resource list_biz_hosts
    # 查询业务下的主机
    list_biz_hosts = bind_property(
        Operation,
        name="list_biz_hosts",
        method="POST",
        path="/api/v3/hosts/app/{bk_biz_id}/list_hosts",
    )

    # bkapi resource list_biz_hosts_topo
    # 查询业务下的主机和拓扑信息
    list_biz_hosts_topo = bind_property(
        Operation,
        name="list_biz_hosts_topo",
        method="POST",
        path="/api/v3/hosts/app/{bk_biz_id}/list_hosts_topo",
    )

    # bkapi resource list_business_in_business_set
    # 查询业务集中的业务列表
    list_business_in_business_set = bind_property(
        Operation,
        name="list_business_in_business_set",
        method="POST",
        path="/api/v3/find/biz_set/biz_list",
    )

    # bkapi resource list_business_set
    # 查询业务集
    list_business_set = bind_property(
        Operation,
        name="list_business_set",
        method="POST",
        path="/api/v3/findmany/biz_set",
    )

    # bkapi resource list_business_set_topo
    # 查询业务集拓扑
    list_business_set_topo = bind_property(
        Operation,
        name="list_business_set_topo",
        method="POST",
        path="/api/v3/find/biz_set/topo_path",
    )

    # bkapi resource list_cached_kube_pod_label_key
    # 获取缓存的Pod的标签键列表
    list_cached_kube_pod_label_key = bind_property(
        Operation,
        name="list_cached_kube_pod_label_key",
        method="POST",
        path="/api/v3/cache/findmany/kube/pod/label/key",
    )

    # bkapi resource list_cached_kube_pod_label_value
    # 获取缓存的Pod的标签键对应的值列表
    list_cached_kube_pod_label_value = bind_property(
        Operation,
        name="list_cached_kube_pod_label_value",
        method="POST",
        path="/api/v3/cache/findmany/kube/pod/label/value",
    )

    # bkapi resource list_cached_res_by_full_sync_cond
    # 根据全量同步缓存条件拉取缓存的资源详情
    list_cached_res_by_full_sync_cond = bind_property(
        Operation,
        name="list_cached_res_by_full_sync_cond",
        method="POST",
        path="/api/v3/cache/findmany/resource/by_full_sync_cond",
    )

    # bkapi resource list_cached_resource_by_ids
    # 根据ID列表拉取缓存的资源详情
    list_cached_resource_by_ids = bind_property(
        Operation,
        name="list_cached_resource_by_ids",
        method="POST",
        path="/api/v3/cache/findmany/resource/by_ids",
    )

    # bkapi resource list_field_template
    # ListFieldTemplate
    list_field_template = bind_property(
        Operation,
        name="list_field_template",
        method="POST",
        path="/api/v3/findmany/field_template",
    )

    # bkapi resource list_field_template_attr
    # ListFieldTemplateAttr
    list_field_template_attr = bind_property(
        Operation,
        name="list_field_template_attr",
        method="POST",
        path="/api/v3/findmany/field_template/attribute",
    )

    # bkapi resource list_full_sync_cond_for_cache
    # 查询全量同步缓存条件
    list_full_sync_cond_for_cache = bind_property(
        Operation,
        name="list_full_sync_cond_for_cache",
        method="POST",
        path="/api/v3/cache/findmany/full/sync/cond",
    )

    # bkapi resource list_host_detail_topology
    # 根据主机条件信息查询主机详情及其所属的拓扑信息
    list_host_detail_topology = bind_property(
        Operation,
        name="list_host_detail_topology",
        method="POST",
        path="/api/v3/findmany/hosts/detail_topo",
    )

    # bkapi resource list_host_related_info
    # 根据主机查询与主机相关的业务及自身详情信息
    list_host_related_info = bind_property(
        Operation,
        name="list_host_related_info",
        method="POST",
        path="/api/v3/sidecar/host/list_host_related_info",
    )

    # bkapi resource list_host_service_template_id
    # 查询主机所属的服务模版id列表信息
    list_host_service_template_id = bind_property(
        Operation,
        name="list_host_service_template_id",
        method="POST",
        path="/api/v3/findmany/hosts/service_template",
    )

    # bkapi resource list_host_total_mainline_topo
    # 查询主机及其对应topo
    list_host_total_mainline_topo = bind_property(
        Operation,
        name="list_host_total_mainline_topo",
        method="POST",
        path="/api/v3/findmany/hosts/total_mainline_topo/biz/{bk_biz_id}",
    )

    # bkapi resource list_hosts_without_biz
    # 没有业务ID的主机查询
    list_hosts_without_biz = bind_property(
        Operation,
        name="list_hosts_without_biz",
        method="POST",
        path="/api/v3/hosts/list_hosts_without_app",
    )

    # bkapi resource list_kube_cluster
    # 查询容器集群
    list_kube_cluster = bind_property(
        Operation,
        name="list_kube_cluster",
        method="POST",
        path="/api/v3/findmany/kube/cluster",
    )

    # bkapi resource list_kube_container
    # 查询Container列表
    list_kube_container = bind_property(
        Operation,
        name="list_kube_container",
        method="POST",
        path="/api/v3/findmany/kube/container",
    )

    # bkapi resource list_kube_container_by_topo
    # 根据容器拓扑获取container信息
    list_kube_container_by_topo = bind_property(
        Operation,
        name="list_kube_container_by_topo",
        method="POST",
        path="/api/v3/findmany/kube/container/by_topo",
    )

    # bkapi resource list_kube_container_for_sec
    # 查询Container列表(安全专用，后续删除)
    list_kube_container_for_sec = bind_property(
        Operation,
        name="list_kube_container_for_sec",
        method="POST",
        path="/api/v3/findmany/kube/container/for_sec",
    )

    # bkapi resource list_kube_namespace
    # 查询namespace
    list_kube_namespace = bind_property(
        Operation,
        name="list_kube_namespace",
        method="POST",
        path="/api/v3/findmany/kube/namespace",
    )

    # bkapi resource list_kube_node
    # 查询容器节点
    list_kube_node = bind_property(
        Operation,
        name="list_kube_node",
        method="POST",
        path="/api/v3/findmany/kube/node",
    )

    # bkapi resource list_kube_pod
    # 查询Pod列表
    list_kube_pod = bind_property(
        Operation,
        name="list_kube_pod",
        method="POST",
        path="/api/v3/findmany/kube/pod",
    )

    # bkapi resource list_kube_pod_for_sec
    # 查询Pod列表(安全专用，后续删除)
    list_kube_pod_for_sec = bind_property(
        Operation,
        name="list_kube_pod_for_sec",
        method="POST",
        path="/api/v3/findmany/kube/pod/for_sec",
    )

    # bkapi resource list_kube_workload
    # 查询workload
    list_kube_workload = bind_property(
        Operation,
        name="list_kube_workload",
        method="POST",
        path="/api/v3/findmany/kube/workload/{kind}",
    )

    # bkapi resource list_obj_field_tmpl_rel
    # ListObjFieldTmplRel
    list_obj_field_tmpl_rel = bind_property(
        Operation,
        name="list_obj_field_tmpl_rel",
        method="POST",
        path="/api/v3/findmany/field_template/object/relation",
    )

    # bkapi resource list_operation_audit
    # 根据条件获取操作审计日志
    list_operation_audit = bind_property(
        Operation,
        name="list_operation_audit",
        method="POST",
        path="/api/v3/findmany/audit_list",
    )

    # bkapi resource list_proc_template
    # 查询进程模板列表
    list_proc_template = bind_property(
        Operation,
        name="list_proc_template",
        method="POST",
        path="/api/v3/findmany/proc/proc_template",
    )

    # bkapi resource list_process_detail_by_ids
    # 查询某业务下进程ID对应的进程详情
    list_process_detail_by_ids = bind_property(
        Operation,
        name="list_process_detail_by_ids",
        method="POST",
        path="/api/v3/findmany/proc/process_instance/detail/biz/{bk_biz_id}",
    )

    # bkapi resource list_process_instance
    # 查询进程实例列表
    list_process_instance = bind_property(
        Operation,
        name="list_process_instance",
        method="POST",
        path="/api/v3/findmany/proc/process_instance",
    )

    # bkapi resource list_process_related_info
    # 点分五位查询进程实例相关信息
    list_process_related_info = bind_property(
        Operation,
        name="list_process_related_info",
        method="POST",
        path="/api/v3/findmany/proc/process_related_info/biz/{bk_biz_id}",
    )

    # bkapi resource list_process_with_vip_info
    # 查询带进程VIP信息的进程实例列表
    list_process_with_vip_info = bind_property(
        Operation,
        name="list_process_with_vip_info",
        method="POST",
        path="/api/v3/findmany/proc/process_instance/with_vip_info",
    )

    # bkapi resource list_project
    # 查询项目
    list_project = bind_property(
        Operation,
        name="list_project",
        method="POST",
        path="/api/v3/findmany/project",
    )

    # bkapi resource list_quoted_inst
    # 查询被引用的模型的实例列表
    list_quoted_inst = bind_property(
        Operation,
        name="list_quoted_inst",
        method="POST",
        path="/api/v3/findmany/quoted/instance",
    )

    # bkapi resource list_resource_pool_hosts
    # 查询资源池中的主机
    list_resource_pool_hosts = bind_property(
        Operation,
        name="list_resource_pool_hosts",
        method="POST",
        path="/api/v3/hosts/list_resource_pool_hosts",
    )

    # bkapi resource list_service_category
    # 查询服务分类列表
    list_service_category = bind_property(
        Operation,
        name="list_service_category",
        method="POST",
        path="/api/v3/findmany/proc/service_category",
    )

    # bkapi resource list_service_instance
    # 查询服务实例列表
    list_service_instance = bind_property(
        Operation,
        name="list_service_instance",
        method="POST",
        path="/api/v3/findmany/proc/service_instance",
    )

    # bkapi resource list_service_instance_by_host
    # 通过主机查询关联的服务实例列表
    list_service_instance_by_host = bind_property(
        Operation,
        name="list_service_instance_by_host",
        method="POST",
        path="/api/v3/findmany/proc/service_instance/with_host",
    )

    # bkapi resource list_service_instance_by_set_template
    # 通过集群模版查询关联的服务实例列表
    list_service_instance_by_set_template = bind_property(
        Operation,
        name="list_service_instance_by_set_template",
        method="POST",
        path="/api/v3/findmany/proc/service/set_template/list_service_instance/biz/{bk_biz_id}",
    )

    # bkapi resource list_service_instance_detail
    # 获取服务实例详细信息
    list_service_instance_detail = bind_property(
        Operation,
        name="list_service_instance_detail",
        method="POST",
        path="/api/v3/findmany/proc/service_instance/details",
    )

    # bkapi resource list_service_template
    # 服务模板列表查询
    list_service_template = bind_property(
        Operation,
        name="list_service_template",
        method="POST",
        path="/api/v3/findmany/proc/service_template",
    )

    # bkapi resource list_service_template_difference
    # 列出服务模版和服务实例之间的差异
    list_service_template_difference = bind_property(
        Operation,
        name="list_service_template_difference",
        method="POST",
        path="/api/v3/findmany/proc/service_template/sync_status/biz/{bk_biz_id}",
    )

    # bkapi resource list_set_template
    # 查询集群模板
    list_set_template = bind_property(
        Operation,
        name="list_set_template",
        method="POST",
        path="/api/v3/findmany/topo/set_template/bk_biz_id/{bk_biz_id}",
    )

    # bkapi resource list_set_template_related_service_template
    # 获取某集群模版下的服务模版列表
    list_set_template_related_service_template = bind_property(
        Operation,
        name="list_set_template_related_service_template",
        method="GET",
        path="/api/v3/findmany/topo/set_template/{set_template_id}/bk_biz_id/{bk_biz_id}/service_templates",
    )

    # bkapi resource post_auth_skip_url
    # post_auth_skip_url
    post_auth_skip_url = bind_property(
        Operation,
        name="post_auth_skip_url",
        method="POST",
        path="/api/v3/auth/skip_url",
    )

    # bkapi resource post_auth_verify
    # post_auth_verify
    post_auth_verify = bind_property(
        Operation,
        name="post_auth_verify",
        method="POST",
        path="/api/v3/auth/verify",
    )

    # bkapi resource post_cloud_account_verify
    # post_cloud_account_verify
    post_cloud_account_verify = bind_property(
        Operation,
        name="post_cloud_account_verify",
        method="POST",
        path="/api/v3/cloud/account/verify",
    )

    # bkapi resource post_count_topoassociationtype
    # post_count_topoassociationtype
    post_count_topoassociationtype = bind_property(
        Operation,
        name="post_count_topoassociationtype",
        method="POST",
        path="/api/v3/count/topoassociationtype",
    )

    # bkapi resource post_count_topoinst_host_service_inst_biz_set
    # post_count_topoinst_host_service_inst_biz_set
    post_count_topoinst_host_service_inst_biz_set = bind_property(
        Operation,
        name="post_count_topoinst_host_service_inst_biz_set",
        method="POST",
        path="/api/v3/count/topoinst/host_service_inst/biz_set/{bk_biz_set_id}",
    )

    # bkapi resource post_create_associationtype
    # post_create_associationtype
    post_create_associationtype = bind_property(
        Operation,
        name="post_create_associationtype",
        method="POST",
        path="/api/v3/create/associationtype",
    )

    # bkapi resource post_create_cloud_account
    # post_create_cloud_account
    post_create_cloud_account = bind_property(
        Operation,
        name="post_create_cloud_account",
        method="POST",
        path="/api/v3/create/cloud/account",
    )

    # bkapi resource post_create_cloud_sync_task
    # post_create_cloud_sync_task
    post_create_cloud_sync_task = bind_property(
        Operation,
        name="post_create_cloud_sync_task",
        method="POST",
        path="/api/v3/create/cloud/sync/task",
    )

    # bkapi resource post_create_field_template
    # post_create_field_template
    post_create_field_template = bind_property(
        Operation,
        name="post_create_field_template",
        method="POST",
        path="/api/v3/create/field_template",
    )

    # bkapi resource post_create_field_template_clone
    # post_create_field_template_clone
    post_create_field_template_clone = bind_property(
        Operation,
        name="post_create_field_template_clone",
        method="POST",
        path="/api/v3/create/field_template/clone",
    )

    # bkapi resource post_create_objectassociation
    # post_create_objectassociation
    post_create_objectassociation = bind_property(
        Operation,
        name="post_create_objectassociation",
        method="POST",
        path="/api/v3/create/objectassociation",
    )

    # bkapi resource post_create_objectattgroup
    # post_create_objectattgroup
    post_create_objectattgroup = bind_property(
        Operation,
        name="post_create_objectattgroup",
        method="POST",
        path="/api/v3/create/objectattgroup",
    )

    # bkapi resource post_create_objectunique_object
    # post_create_objectunique_object
    post_create_objectunique_object = bind_property(
        Operation,
        name="post_create_objectunique_object",
        method="POST",
        path="/api/v3/create/objectunique/object/{bk_obj_id}",
    )

    # bkapi resource post_create_operation_chart
    # post_create_operation_chart
    post_create_operation_chart = bind_property(
        Operation,
        name="post_create_operation_chart",
        method="POST",
        path="/api/v3/create/operation/chart",
    )

    # bkapi resource post_create_proc_service_template_all_info
    # post_create_proc_service_template_all_info
    post_create_proc_service_template_all_info = bind_property(
        Operation,
        name="post_create_proc_service_template_all_info",
        method="POST",
        path="/api/v3/create/proc/service_template/all_info",
    )

    # bkapi resource post_create_resource_directory
    # post_create_resource_directory
    post_create_resource_directory = bind_property(
        Operation,
        name="post_create_resource_directory",
        method="POST",
        path="/api/v3/create/resource/directory",
    )

    # bkapi resource post_create_topo_set_template_all_info
    # post_create_topo_set_template_all_info
    post_create_topo_set_template_all_info = bind_property(
        Operation,
        name="post_create_topo_set_template_all_info",
        method="POST",
        path="/api/v3/create/topo/set_template/all_info",
    )

    # bkapi resource post_create_topomodelmainline
    # post_create_topomodelmainline
    post_create_topomodelmainline = bind_property(
        Operation,
        name="post_create_topomodelmainline",
        method="POST",
        path="/api/v3/create/topomodelmainline",
    )

    # bkapi resource post_createmany_cloudarea
    # post_createmany_cloudarea
    post_createmany_cloudarea = bind_property(
        Operation,
        name="post_createmany_cloudarea",
        method="POST",
        path="/api/v3/createmany/cloudarea",
    )

    # bkapi resource post_delete_objectunique_object__unique
    # post_delete_objectunique_object__unique
    post_delete_objectunique_object__unique = bind_property(
        Operation,
        name="post_delete_objectunique_object__unique",
        method="POST",
        path="/api/v3/delete/objectunique/object/{bk_obj_id}/unique/{id}",
    )

    # bkapi resource post_find_associationtype
    # post_find_associationtype
    post_find_associationtype = bind_property(
        Operation,
        name="post_find_associationtype",
        method="POST",
        path="/api/v3/find/associationtype",
    )

    # bkapi resource post_find_biz_set_preview
    # post_find_biz_set_preview
    post_find_biz_set_preview = bind_property(
        Operation,
        name="post_find_biz_set_preview",
        method="POST",
        path="/api/v3/find/biz_set/preview",
    )

    # bkapi resource post_find_classificationobject
    # post_find_classificationobject
    post_find_classificationobject = bind_property(
        Operation,
        name="post_find_classificationobject",
        method="POST",
        path="/api/v3/find/classificationobject",
    )

    # bkapi resource post_find_field_template_attribute_difference
    # post_find_field_template_attribute_difference
    post_find_field_template_attribute_difference = bind_property(
        Operation,
        name="post_find_field_template_attribute_difference",
        method="POST",
        path="/api/v3/find/field_template/attribute/difference",
    )

    # bkapi resource post_find_field_template_model_status
    # post_find_field_template_model_status
    post_find_field_template_model_status = bind_property(
        Operation,
        name="post_find_field_template_model_status",
        method="POST",
        path="/api/v3/find/field_template/model/status",
    )

    # bkapi resource post_find_field_template_simplify_by_attr_template_id
    # post_find_field_template_simplify_by_attr_template_id
    post_find_field_template_simplify_by_attr_template_id = bind_property(
        Operation,
        name="post_find_field_template_simplify_by_attr_template_id",
        method="POST",
        path="/api/v3/find/field_template/simplify/by_attr_template_id",
    )

    # bkapi resource post_find_field_template_sync_status
    # post_find_field_template_sync_status
    post_find_field_template_sync_status = bind_property(
        Operation,
        name="post_find_field_template_sync_status",
        method="POST",
        path="/api/v3/find/field_template/sync/status",
    )

    # bkapi resource post_find_field_template_tasks_status
    # post_find_field_template_tasks_status
    post_find_field_template_tasks_status = bind_property(
        Operation,
        name="post_find_field_template_tasks_status",
        method="POST",
        path="/api/v3/find/field_template/tasks_status",
    )

    # bkapi resource post_find_field_template_unique_difference
    # post_find_field_template_unique_difference
    post_find_field_template_unique_difference = bind_property(
        Operation,
        name="post_find_field_template_unique_difference",
        method="POST",
        path="/api/v3/find/field_template/unique/difference",
    )

    # bkapi resource post_find_full_text
    # post_find_full_text
    post_find_full_text = bind_property(
        Operation,
        name="post_find_full_text",
        method="POST",
        path="/api/v3/find/full_text",
    )

    # bkapi resource post_find_host_topopath
    # post_find_host_topopath
    post_find_host_topopath = bind_property(
        Operation,
        name="post_find_host_topopath",
        method="POST",
        path="/api/v3/find/host/topopath",
    )

    # bkapi resource post_find_inst_audit
    # post_find_inst_audit
    post_find_inst_audit = bind_property(
        Operation,
        name="post_find_inst_audit",
        method="POST",
        path="/api/v3/find/inst_audit",
    )

    # bkapi resource post_find_instassociation_biz
    # post_find_instassociation_biz
    post_find_instassociation_biz = bind_property(
        Operation,
        name="post_find_instassociation_biz",
        method="POST",
        path="/api/v3/find/instassociation/biz/{bk_biz_id}",
    )

    # bkapi resource post_find_kube_host_node_path
    # post_find_kube_host_node_path
    post_find_kube_host_node_path = bind_property(
        Operation,
        name="post_find_kube_host_node_path",
        method="POST",
        path="/api/v3/find/kube/host_node_path",
    )

    # bkapi resource post_find_kube_pod_path
    # post_find_kube_pod_path
    post_find_kube_pod_path = bind_property(
        Operation,
        name="post_find_kube_pod_path",
        method="POST",
        path="/api/v3/find/kube/pod_path",
    )

    # bkapi resource post_find_kube_topo_node_count
    # post_find_kube_topo_node_count
    post_find_kube_topo_node_count = bind_property(
        Operation,
        name="post_find_kube_topo_node_count",
        method="POST",
        path="/api/v3/find/kube/topo_node/{type}/count",
    )

    # bkapi resource post_find_kube_topo_path
    # post_find_kube_topo_path
    post_find_kube_topo_path = bind_property(
        Operation,
        name="post_find_kube_topo_path",
        method="POST",
        path="/api/v3/find/kube/topo_path",
    )

    # bkapi resource post_find_objecttopo_scope_type_global_scope_id_0
    # post_find_objecttopo_scope_type_global_scope_id_0
    post_find_objecttopo_scope_type_global_scope_id_0 = bind_property(
        Operation,
        name="post_find_objecttopo_scope_type_global_scope_id_0",
        method="POST",
        path="/api/v3/find/objecttopo/scope_type/global/scope_id/0",
    )

    # bkapi resource post_find_operation_chart_data
    # post_find_operation_chart_data
    post_find_operation_chart_data = bind_property(
        Operation,
        name="post_find_operation_chart_data",
        method="POST",
        path="/api/v3/find/operation/chart/data",
    )

    # bkapi resource post_find_proc_biz_set__proc_template_id
    # post_find_proc_biz_set__proc_template_id
    post_find_proc_biz_set__proc_template_id = bind_property(
        Operation,
        name="post_find_proc_biz_set__proc_template_id",
        method="POST",
        path="/api/v3/find/proc/biz_set/{bk_biz_set_id}/proc_template/id/{process_template_id}",
    )

    # bkapi resource post_find_proc_difference_service_instances
    # post_find_proc_difference_service_instances
    post_find_proc_difference_service_instances = bind_property(
        Operation,
        name="post_find_proc_difference_service_instances",
        method="POST",
        path="/api/v3/find/proc/difference/service_instances",
    )

    # bkapi resource post_find_proc_service_instance_difference_detail
    # post_find_proc_service_instance_difference_detail
    post_find_proc_service_instance_difference_detail = bind_property(
        Operation,
        name="post_find_proc_service_instance_difference_detail",
        method="POST",
        path="/api/v3/find/proc/service_instance/difference_detail",
    )

    # bkapi resource post_find_proc_service_template_all_info
    # post_find_proc_service_template_all_info
    post_find_proc_service_template_all_info = bind_property(
        Operation,
        name="post_find_proc_service_template_all_info",
        method="POST",
        path="/api/v3/find/proc/service_template/all_info",
    )

    # bkapi resource post_find_proc_service_template_general_difference
    # post_find_proc_service_template_general_difference
    post_find_proc_service_template_general_difference = bind_property(
        Operation,
        name="post_find_proc_service_template_general_difference",
        method="POST",
        path="/api/v3/find/proc/service_template/general_difference",
    )

    # bkapi resource post_find_proc_service_template_host_apply_rule_related
    # post_find_proc_service_template_host_apply_rule_related
    post_find_proc_service_template_host_apply_rule_related = bind_property(
        Operation,
        name="post_find_proc_service_template_host_apply_rule_related",
        method="POST",
        path="/api/v3/find/proc/service_template/host_apply_rule_related",
    )

    # bkapi resource post_find_topo_set_template_all_info
    # post_find_topo_set_template_all_info
    post_find_topo_set_template_all_info = bind_property(
        Operation,
        name="post_find_topo_set_template_all_info",
        method="POST",
        path="/api/v3/find/topo/set_template/all_info",
    )

    # bkapi resource post_find_topoinst_bk_biz_id__host_apply_rule_related
    # post_find_topoinst_bk_biz_id__host_apply_rule_related
    post_find_topoinst_bk_biz_id__host_apply_rule_related = bind_property(
        Operation,
        name="post_find_topoinst_bk_biz_id__host_apply_rule_related",
        method="POST",
        path="/api/v3/find/topoinst/bk_biz_id/{bk_biz_id}/host_apply_rule_related",
    )

    # bkapi resource post_find_topoinst_with_statistics_biz
    # post_find_topoinst_with_statistics_biz
    post_find_topoinst_with_statistics_biz = bind_property(
        Operation,
        name="post_find_topoinst_with_statistics_biz",
        method="POST",
        path="/api/v3/find/topoinst_with_statistics/biz/{bk_biz_id}",
    )

    # bkapi resource post_find_topoinstnode_host_serviceinst_count
    # post_find_topoinstnode_host_serviceinst_count
    post_find_topoinstnode_host_serviceinst_count = bind_property(
        Operation,
        name="post_find_topoinstnode_host_serviceinst_count",
        method="POST",
        path="/api/v3/find/topoinstnode/host_serviceinst_count/{bk_biz_id}",
    )

    # bkapi resource post_find_topopath_biz
    # post_find_topopath_biz
    post_find_topopath_biz = bind_property(
        Operation,
        name="post_find_topopath_biz",
        method="POST",
        path="/api/v3/find/topopath/biz/{bk_biz_id}",
    )

    # bkapi resource post_find_topopath_biz_set__biz
    # post_find_topopath_biz_set__biz
    post_find_topopath_biz_set__biz = bind_property(
        Operation,
        name="post_find_topopath_biz_set__biz",
        method="POST",
        path="/api/v3/find/topopath/biz_set/{bk_biz_set_id}/biz/{bk_biz_id}",
    )

    # bkapi resource post_findmany_cloud_account
    # post_findmany_cloud_account
    post_findmany_cloud_account = bind_property(
        Operation,
        name="post_findmany_cloud_account",
        method="POST",
        path="/api/v3/findmany/cloud/account",
    )

    # bkapi resource post_findmany_cloud_account_validity
    # post_findmany_cloud_account_validity
    post_findmany_cloud_account_validity = bind_property(
        Operation,
        name="post_findmany_cloud_account_validity",
        method="POST",
        path="/api/v3/findmany/cloud/account/validity",
    )

    # bkapi resource post_findmany_cloud_account_vpc
    # post_findmany_cloud_account_vpc
    post_findmany_cloud_account_vpc = bind_property(
        Operation,
        name="post_findmany_cloud_account_vpc",
        method="POST",
        path="/api/v3/findmany/cloud/account/vpc/{id}",
    )

    # bkapi resource post_findmany_cloud_sync_history
    # post_findmany_cloud_sync_history
    post_findmany_cloud_sync_history = bind_property(
        Operation,
        name="post_findmany_cloud_sync_history",
        method="POST",
        path="/api/v3/findmany/cloud/sync/history",
    )

    # bkapi resource post_findmany_cloud_sync_region
    # post_findmany_cloud_sync_region
    post_findmany_cloud_sync_region = bind_property(
        Operation,
        name="post_findmany_cloud_sync_region",
        method="POST",
        path="/api/v3/findmany/cloud/sync/region",
    )

    # bkapi resource post_findmany_cloud_sync_task
    # post_findmany_cloud_sync_task
    post_findmany_cloud_sync_task = bind_property(
        Operation,
        name="post_findmany_cloud_sync_task",
        method="POST",
        path="/api/v3/findmany/cloud/sync/task",
    )

    # bkapi resource post_findmany_cloudarea_hostcount
    # post_findmany_cloudarea_hostcount
    post_findmany_cloudarea_hostcount = bind_property(
        Operation,
        name="post_findmany_cloudarea_hostcount",
        method="POST",
        path="/api/v3/findmany/cloudarea/hostcount",
    )

    # bkapi resource post_findmany_field_template_attribute_count
    # post_findmany_field_template_attribute_count
    post_findmany_field_template_attribute_count = bind_property(
        Operation,
        name="post_findmany_field_template_attribute_count",
        method="POST",
        path="/api/v3/findmany/field_template/attribute/count",
    )

    # bkapi resource post_findmany_field_template_by_object
    # post_findmany_field_template_by_object
    post_findmany_field_template_by_object = bind_property(
        Operation,
        name="post_findmany_field_template_by_object",
        method="POST",
        path="/api/v3/findmany/field_template/by_object",
    )

    # bkapi resource post_findmany_field_template_object_count
    # post_findmany_field_template_object_count
    post_findmany_field_template_object_count = bind_property(
        Operation,
        name="post_findmany_field_template_object_count",
        method="POST",
        path="/api/v3/findmany/field_template/object/count",
    )

    # bkapi resource post_findmany_field_template_unique
    # post_findmany_field_template_unique
    post_findmany_field_template_unique = bind_property(
        Operation,
        name="post_findmany_field_template_unique",
        method="POST",
        path="/api/v3/findmany/field_template/unique",
    )

    # bkapi resource post_findmany_host_apply_rule_bk_biz_id
    # post_findmany_host_apply_rule_bk_biz_id
    post_findmany_host_apply_rule_bk_biz_id = bind_property(
        Operation,
        name="post_findmany_host_apply_rule_bk_biz_id",
        method="POST",
        path="/api/v3/findmany/host_apply_rule/bk_biz_id/{bk_biz_id}",
    )

    # bkapi resource post_findmany_host_apply_rule_bk_biz_id__host_related_rules
    # post_findmany_host_apply_rule_bk_biz_id__host_related_rules
    post_findmany_host_apply_rule_bk_biz_id__host_related_rules = bind_property(
        Operation,
        name="post_findmany_host_apply_rule_bk_biz_id__host_related_rules",
        method="POST",
        path="/api/v3/findmany/host_apply_rule/bk_biz_id/{bk_biz_id}/host_related_rules",
    )

    # bkapi resource post_findmany_hosts_biz_set
    # post_findmany_hosts_biz_set
    post_findmany_hosts_biz_set = bind_property(
        Operation,
        name="post_findmany_hosts_biz_set",
        method="POST",
        path="/api/v3/findmany/hosts/biz_set/{bk_biz_set_id}",
    )

    # bkapi resource post_findmany_hosts_search_noauth
    # post_findmany_hosts_search_noauth
    post_findmany_hosts_search_noauth = bind_property(
        Operation,
        name="post_findmany_hosts_search_noauth",
        method="POST",
        path="/api/v3/findmany/hosts/search/noauth",
    )

    # bkapi resource post_findmany_hosts_search_resource
    # post_findmany_hosts_search_resource
    post_findmany_hosts_search_resource = bind_property(
        Operation,
        name="post_findmany_hosts_search_resource",
        method="POST",
        path="/api/v3/findmany/hosts/search/resource",
    )

    # bkapi resource post_findmany_hosts_search_with_biz
    # post_findmany_hosts_search_with_biz
    post_findmany_hosts_search_with_biz = bind_property(
        Operation,
        name="post_findmany_hosts_search_with_biz",
        method="POST",
        path="/api/v3/findmany/hosts/search/with_biz",
    )

    # bkapi resource post_findmany_inst_association_object__inst_id__offset__limit__web
    # post_findmany_inst_association_object__inst_id__offset__limit__web
    post_findmany_inst_association_object__inst_id__offset__limit__web = bind_property(
        Operation,
        name="post_findmany_inst_association_object__inst_id__offset__limit__web",
        method="POST",
        path="/api/v3/findmany/inst/association/object/{bk_obj_id}/inst_id/{bk_inst_id}/offset/{offset}/limit/{limit}/web",  # noqa
    )

    # bkapi resource post_findmany_module_biz_set__biz__set
    # post_findmany_module_biz_set__biz__set
    post_findmany_module_biz_set__biz__set = bind_property(
        Operation,
        name="post_findmany_module_biz_set__biz__set",
        method="POST",
        path="/api/v3/findmany/module/biz_set/{bk_biz_set_id}/biz/{bk_biz_id}/set/{bk_set_id}",
    )

    # bkapi resource post_findmany_object_by_field_template
    # post_findmany_object_by_field_template
    post_findmany_object_by_field_template = bind_property(
        Operation,
        name="post_findmany_object_by_field_template",
        method="POST",
        path="/api/v3/findmany/object/by_field_template",
    )

    # bkapi resource post_findmany_object_instances_names
    # post_findmany_object_instances_names
    post_findmany_object_instances_names = bind_property(
        Operation,
        name="post_findmany_object_instances_names",
        method="POST",
        path="/api/v3/findmany/object/instances/names",
    )

    # bkapi resource post_findmany_proc_biz_set__proc_template
    # post_findmany_proc_biz_set__proc_template
    post_findmany_proc_biz_set__proc_template = bind_property(
        Operation,
        name="post_findmany_proc_biz_set__proc_template",
        method="POST",
        path="/api/v3/findmany/proc/biz_set/{bk_biz_set_id}/proc_template",
    )

    # bkapi resource post_findmany_proc_biz_set__process_instance
    # post_findmany_proc_biz_set__process_instance
    post_findmany_proc_biz_set__process_instance = bind_property(
        Operation,
        name="post_findmany_proc_biz_set__process_instance",
        method="POST",
        path="/api/v3/findmany/proc/biz_set/{bk_biz_set_id}/process_instance",
    )

    # bkapi resource post_findmany_proc_biz_set__process_instance_detail_by_ids
    # post_findmany_proc_biz_set__process_instance_detail_by_ids
    post_findmany_proc_biz_set__process_instance_detail_by_ids = bind_property(
        Operation,
        name="post_findmany_proc_biz_set__process_instance_detail_by_ids",
        method="POST",
        path="/api/v3/findmany/proc/biz_set/{bk_biz_set_id}/process_instance/detail/by_ids",
    )

    # bkapi resource post_findmany_proc_biz_set__process_instance_name_ids
    # post_findmany_proc_biz_set__process_instance_name_ids
    post_findmany_proc_biz_set__process_instance_name_ids = bind_property(
        Operation,
        name="post_findmany_proc_biz_set__process_instance_name_ids",
        method="POST",
        path="/api/v3/findmany/proc/biz_set/{bk_biz_set_id}/process_instance/name_ids",
    )

    # bkapi resource post_findmany_proc_biz_set__service_instance_labels_aggregation
    # post_findmany_proc_biz_set__service_instance_labels_aggregation
    post_findmany_proc_biz_set__service_instance_labels_aggregation = bind_property(
        Operation,
        name="post_findmany_proc_biz_set__service_instance_labels_aggregation",
        method="POST",
        path="/api/v3/findmany/proc/biz_set/{bk_biz_set_id}/service_instance/labels/aggregation",
    )

    # bkapi resource post_findmany_proc_biz_set_service_instance
    # post_findmany_proc_biz_set_service_instance
    post_findmany_proc_biz_set_service_instance = bind_property(
        Operation,
        name="post_findmany_proc_biz_set_service_instance",
        method="POST",
        path="/api/v3/findmany/proc/biz_set/{bk_biz_set_id}/service_instance",
    )

    # bkapi resource post_findmany_proc_biz_set_service_instance_with_host
    # post_findmany_proc_biz_set_service_instance_with_host
    post_findmany_proc_biz_set_service_instance_with_host = bind_property(
        Operation,
        name="post_findmany_proc_biz_set_service_instance_with_host",
        method="POST",
        path="/api/v3/findmany/proc/biz_set/{bk_biz_set_id}/service_instance/with_host",
    )

    # bkapi resource post_findmany_proc_host_with_no_service_instance
    # post_findmany_proc_host_with_no_service_instance
    post_findmany_proc_host_with_no_service_instance = bind_property(
        Operation,
        name="post_findmany_proc_host_with_no_service_instance",
        method="POST",
        path="/api/v3/findmany/proc/host/with_no_service_instance",
    )

    # bkapi resource post_findmany_proc_process_instance_detail_by_ids
    # post_findmany_proc_process_instance_detail_by_ids
    post_findmany_proc_process_instance_detail_by_ids = bind_property(
        Operation,
        name="post_findmany_proc_process_instance_detail_by_ids",
        method="POST",
        path="/api/v3/findmany/proc/process_instance/detail/by_ids",
    )

    # bkapi resource post_findmany_proc_process_instance_name_ids
    # post_findmany_proc_process_instance_name_ids
    post_findmany_proc_process_instance_name_ids = bind_property(
        Operation,
        name="post_findmany_proc_process_instance_name_ids",
        method="POST",
        path="/api/v3/findmany/proc/process_instance/name_ids",
    )

    # bkapi resource post_findmany_proc_service_category_with_statistics
    # post_findmany_proc_service_category_with_statistics
    post_findmany_proc_service_category_with_statistics = bind_property(
        Operation,
        name="post_findmany_proc_service_category_with_statistics",
        method="POST",
        path="/api/v3/findmany/proc/service_category/with_statistics",
    )

    # bkapi resource post_findmany_proc_service_instance_labels_aggregation
    # post_findmany_proc_service_instance_labels_aggregation
    post_findmany_proc_service_instance_labels_aggregation = bind_property(
        Operation,
        name="post_findmany_proc_service_instance_labels_aggregation",
        method="POST",
        path="/api/v3/findmany/proc/service_instance/labels/aggregation",
    )

    # bkapi resource post_findmany_proc_service_template_attribute
    # post_findmany_proc_service_template_attribute
    post_findmany_proc_service_template_attribute = bind_property(
        Operation,
        name="post_findmany_proc_service_template_attribute",
        method="POST",
        path="/api/v3/findmany/proc/service_template/attribute",
    )

    # bkapi resource post_findmany_proc_service_template_count_info_biz
    # post_findmany_proc_service_template_count_info_biz
    post_findmany_proc_service_template_count_info_biz = bind_property(
        Operation,
        name="post_findmany_proc_service_template_count_info_biz",
        method="POST",
        path="/api/v3/findmany/proc/service_template/count_info/biz/{bk_biz_id}",
    )

    # bkapi resource post_findmany_proc_service_template_host_apply_plan_status
    # post_findmany_proc_service_template_host_apply_plan_status
    post_findmany_proc_service_template_host_apply_plan_status = bind_property(
        Operation,
        name="post_findmany_proc_service_template_host_apply_plan_status",
        method="POST",
        path="/api/v3/findmany/proc/service_template/host_apply_plan/status",
    )

    # bkapi resource post_findmany_proc_service_template_sync_status_bk_biz_id
    # post_findmany_proc_service_template_sync_status_bk_biz_id
    post_findmany_proc_service_template_sync_status_bk_biz_id = bind_property(
        Operation,
        name="post_findmany_proc_service_template_sync_status_bk_biz_id",
        method="POST",
        path="/api/v3/findmany/proc/service_template_sync_status/bk_biz_id/{bk_biz_id}",
    )

    # bkapi resource post_findmany_resource_directory
    # post_findmany_resource_directory
    post_findmany_resource_directory = bind_property(
        Operation,
        name="post_findmany_resource_directory",
        method="POST",
        path="/api/v3/findmany/resource/directory",
    )

    # bkapi resource post_findmany_set_biz_set__biz
    # post_findmany_set_biz_set__biz
    post_findmany_set_biz_set__biz = bind_property(
        Operation,
        name="post_findmany_set_biz_set__biz",
        method="POST",
        path="/api/v3/findmany/set/biz_set/{bk_biz_set_id}/biz/{bk_biz_id}",
    )

    # bkapi resource post_findmany_topo_set_template__bk_biz_id__diff_with_instances
    # post_findmany_topo_set_template__bk_biz_id__diff_with_instances
    post_findmany_topo_set_template__bk_biz_id__diff_with_instances = bind_property(
        Operation,
        name="post_findmany_topo_set_template__bk_biz_id__diff_with_instances",
        method="POST",
        path="/api/v3/findmany/topo/set_template/{set_template_id}/bk_biz_id/{bk_biz_id}/diff_with_instances",
    )

    # bkapi resource post_findmany_topo_set_template__bk_biz_id__host_with_instances
    # post_findmany_topo_set_template__bk_biz_id__host_with_instances
    post_findmany_topo_set_template__bk_biz_id__host_with_instances = bind_property(
        Operation,
        name="post_findmany_topo_set_template__bk_biz_id__host_with_instances",
        method="POST",
        path="/api/v3/findmany/topo/set_template/{templateId}/bk_biz_id/{bk_biz_id}/host_with_instances",
    )

    # bkapi resource post_findmany_topo_set_template__bk_biz_id__instances_sync_status
    # post_findmany_topo_set_template__bk_biz_id__instances_sync_status
    post_findmany_topo_set_template__bk_biz_id__instances_sync_status = bind_property(
        Operation,
        name="post_findmany_topo_set_template__bk_biz_id__instances_sync_status",
        method="POST",
        path="/api/v3/findmany/topo/set_template/{set_template_id}/bk_biz_id/{bk_biz_id}/instances_sync_status",
    )

    # bkapi resource post_findmany_topo_set_template__bk_biz_id__sets_web
    # post_findmany_topo_set_template__bk_biz_id__sets_web
    post_findmany_topo_set_template__bk_biz_id__sets_web = bind_property(
        Operation,
        name="post_findmany_topo_set_template__bk_biz_id__sets_web",
        method="POST",
        path="/api/v3/findmany/topo/set_template/{set_template_id}/bk_biz_id/{bk_biz_id}/sets/web",
    )

    # bkapi resource post_findmany_topo_set_template_attribute
    # post_findmany_topo_set_template_attribute
    post_findmany_topo_set_template_attribute = bind_property(
        Operation,
        name="post_findmany_topo_set_template_attribute",
        method="POST",
        path="/api/v3/findmany/topo/set_template/attribute",
    )

    # bkapi resource post_findmany_topo_set_template_bk_biz_id__set_template_status
    # post_findmany_topo_set_template_bk_biz_id__set_template_status
    post_findmany_topo_set_template_bk_biz_id__set_template_status = bind_property(
        Operation,
        name="post_findmany_topo_set_template_bk_biz_id__set_template_status",
        method="POST",
        path="/api/v3/findmany/topo/set_template/bk_biz_id/{bk_biz_id}/set_template_status",
    )

    # bkapi resource post_findmany_topo_set_template_bk_biz_id__web
    # post_findmany_topo_set_template_bk_biz_id__web
    post_findmany_topo_set_template_bk_biz_id__web = bind_property(
        Operation,
        name="post_findmany_topo_set_template_bk_biz_id__web",
        method="POST",
        path="/api/v3/findmany/topo/set_template/bk_biz_id/{bk_biz_id}/web",
    )

    # bkapi resource post_findmany_topo_set_template_sync_history_bk_biz_id
    # post_findmany_topo_set_template_sync_history_bk_biz_id
    post_findmany_topo_set_template_sync_history_bk_biz_id = bind_property(
        Operation,
        name="post_findmany_topo_set_template_sync_history_bk_biz_id",
        method="POST",
        path="/api/v3/findmany/topo/set_template_sync_history/bk_biz_id/{bk_biz_id}",
    )

    # bkapi resource post_findmany_topo_set_template_sync_status_bk_biz_id
    # post_findmany_topo_set_template_sync_status_bk_biz_id
    post_findmany_topo_set_template_sync_status_bk_biz_id = bind_property(
        Operation,
        name="post_findmany_topo_set_template_sync_status_bk_biz_id",
        method="POST",
        path="/api/v3/findmany/topo/set_template_sync_status/bk_biz_id/{bk_biz_id}",
    )

    # bkapi resource post_host_createmany_module_host_apply_plan_preview
    # post_host_createmany_module_host_apply_plan_preview
    post_host_createmany_module_host_apply_plan_preview = bind_property(
        Operation,
        name="post_host_createmany_module_host_apply_plan_preview",
        method="POST",
        path="/api/v3/host/createmany/module/host_apply_plan/preview",
    )

    # bkapi resource post_host_createmany_service_template_host_apply_plan_preview
    # post_host_createmany_service_template_host_apply_plan_preview
    post_host_createmany_service_template_host_apply_plan_preview = bind_property(
        Operation,
        name="post_host_createmany_service_template_host_apply_plan_preview",
        method="POST",
        path="/api/v3/host/createmany/service_template/host_apply_plan/preview",
    )

    # bkapi resource post_host_find_service_template_host_apply_status
    # post_host_find_service_template_host_apply_status
    post_host_find_service_template_host_apply_status = bind_property(
        Operation,
        name="post_host_find_service_template_host_apply_status",
        method="POST",
        path="/api/v3/host/find/service_template/host_apply_status",
    )

    # bkapi resource post_host_findmany_module_get_module_final_rules
    # post_host_findmany_module_get_module_final_rules
    post_host_findmany_module_get_module_final_rules = bind_property(
        Operation,
        name="post_host_findmany_module_get_module_final_rules",
        method="POST",
        path="/api/v3/host/findmany/module/get_module_final_rules",
    )

    # bkapi resource post_host_findmany_module_host_apply_plan_invalid_host_count
    # post_host_findmany_module_host_apply_plan_invalid_host_count
    post_host_findmany_module_host_apply_plan_invalid_host_count = bind_property(
        Operation,
        name="post_host_findmany_module_host_apply_plan_invalid_host_count",
        method="POST",
        path="/api/v3/host/findmany/module/host_apply_plan/invalid_host_count",
    )

    # bkapi resource post_host_findmany_module_host_apply_plan_status
    # post_host_findmany_module_host_apply_plan_status
    post_host_findmany_module_host_apply_plan_status = bind_property(
        Operation,
        name="post_host_findmany_module_host_apply_plan_status",
        method="POST",
        path="/api/v3/host/findmany/module/host_apply_plan/status",
    )

    # bkapi resource post_host_findmany_service_template_host_apply_plan_invalid_host_count
    # post_host_findmany_service_template_host_apply_plan_invalid_host_count
    post_host_findmany_service_template_host_apply_plan_invalid_host_count = bind_property(
        Operation,
        name="post_host_findmany_service_template_host_apply_plan_invalid_host_count",
        method="POST",
        path="/api/v3/host/findmany/service_template/host_apply_plan/invalid_host_count",
    )

    # bkapi resource post_host_findmany_service_template_host_apply_rule
    # post_host_findmany_service_template_host_apply_rule
    post_host_findmany_service_template_host_apply_rule = bind_property(
        Operation,
        name="post_host_findmany_service_template_host_apply_rule",
        method="POST",
        path="/api/v3/host/findmany/service_template/host_apply_rule",
    )

    # bkapi resource post_host_findmany_service_template_host_apply_rule_count
    # post_host_findmany_service_template_host_apply_rule_count
    post_host_findmany_service_template_host_apply_rule_count = bind_property(
        Operation,
        name="post_host_findmany_service_template_host_apply_rule_count",
        method="POST",
        path="/api/v3/host/findmany/service_template/host_apply_rule_count",
    )

    # bkapi resource post_host_transfer_resource_directory
    # post_host_transfer_resource_directory
    post_host_transfer_resource_directory = bind_property(
        Operation,
        name="post_host_transfer_resource_directory",
        method="POST",
        path="/api/v3/host/transfer/resource/directory",
    )

    # bkapi resource post_host_transfer_with_auto_clear_service_instance_bk_biz_id
    # post_host_transfer_with_auto_clear_service_instance_bk_biz_id
    post_host_transfer_with_auto_clear_service_instance_bk_biz_id = bind_property(
        Operation,
        name="post_host_transfer_with_auto_clear_service_instance_bk_biz_id",
        method="POST",
        path="/api/v3/host/transfer_with_auto_clear_service_instance/bk_biz_id/{bk_biz_id}",
    )

    # bkapi resource post_host_transfer_with_auto_clear_service_instance_bk_biz_id__preview
    # post_host_transfer_with_auto_clear_service_instance_bk_biz_id__preview
    post_host_transfer_with_auto_clear_service_instance_bk_biz_id__preview = bind_property(
        Operation,
        name="post_host_transfer_with_auto_clear_service_instance_bk_biz_id__preview",
        method="POST",
        path="/api/v3/host/transfer_with_auto_clear_service_instance/bk_biz_id/{bk_biz_id}/preview",
    )

    # bkapi resource post_host_updatemany_module_host_apply_plan_run
    # post_host_updatemany_module_host_apply_plan_run
    post_host_updatemany_module_host_apply_plan_run = bind_property(
        Operation,
        name="post_host_updatemany_module_host_apply_plan_run",
        method="POST",
        path="/api/v3/host/updatemany/module/host_apply_plan/run",
    )

    # bkapi resource post_hosts_favorites
    # post_hosts_favorites
    post_hosts_favorites = bind_property(
        Operation,
        name="post_hosts_favorites",
        method="POST",
        path="/api/v3/hosts/favorites",
    )

    # bkapi resource post_hosts_favorites_search
    # post_hosts_favorites_search
    post_hosts_favorites_search = bind_property(
        Operation,
        name="post_hosts_favorites_search",
        method="POST",
        path="/api/v3/hosts/favorites/search",
    )

    # bkapi resource post_hosts_import
    # post_hosts_import
    post_hosts_import = bind_property(
        Operation,
        name="post_hosts_import",
        method="POST",
        path="/api/v3/hosts/import",
    )

    # bkapi resource post_hosts_kube_search
    # post_hosts_kube_search
    post_hosts_kube_search = bind_property(
        Operation,
        name="post_hosts_kube_search",
        method="POST",
        path="/api/v3/hosts/kube/search",
    )

    # bkapi resource post_hosts_modules_biz_mutilple
    # post_hosts_modules_biz_mutilple
    post_hosts_modules_biz_mutilple = bind_property(
        Operation,
        name="post_hosts_modules_biz_mutilple",
        method="POST",
        path="/api/v3/hosts/modules/biz/mutilple",
    )

    # bkapi resource post_hosts_resource_cross_biz
    # post_hosts_resource_cross_biz
    post_hosts_resource_cross_biz = bind_property(
        Operation,
        name="post_hosts_resource_cross_biz",
        method="POST",
        path="/api/v3/hosts/resource/cross/biz",
    )

    # bkapi resource post_hosts_search
    # post_hosts_search
    post_hosts_search = bind_property(
        Operation,
        name="post_hosts_search",
        method="POST",
        path="/api/v3/hosts/search",
    )

    # bkapi resource post_module_bk_biz_id__service_template_id
    # post_module_bk_biz_id__service_template_id
    post_module_bk_biz_id__service_template_id = bind_property(
        Operation,
        name="post_module_bk_biz_id__service_template_id",
        method="POST",
        path="/api/v3/module/bk_biz_id/{bk_biz_id}/service_template_id/{service_template_id}",
    )

    # bkapi resource post_set__batch
    # post_set__batch
    post_set__batch = bind_property(
        Operation,
        name="post_set__batch",
        method="POST",
        path="/api/v3/set/{bk_biz_id}/batch",
    )

    # bkapi resource post_shipper_find_srv_status_scene_type
    # post_shipper_find_srv_status_scene_type
    post_shipper_find_srv_status_scene_type = bind_property(
        Operation,
        name="post_shipper_find_srv_status_scene_type",
        method="POST",
        path="/api/v3/shipper/find/srv_status/scene_type",
    )

    # bkapi resource post_shipper_findmany_special_biz
    # post_shipper_findmany_special_biz
    post_shipper_findmany_special_biz = bind_property(
        Operation,
        name="post_shipper_findmany_special_biz",
        method="POST",
        path="/api/v3/shipper/findmany/special/biz",
    )

    # bkapi resource post_shipper_sync_nieg_host
    # post_shipper_sync_nieg_host
    post_shipper_sync_nieg_host = bind_property(
        Operation,
        name="post_shipper_sync_nieg_host",
        method="POST",
        path="/api/v3/shipper/sync/nieg/host",
    )

    # bkapi resource post_sidecar_delete_nieg_host
    # post_sidecar_delete_nieg_host
    post_sidecar_delete_nieg_host = bind_property(
        Operation,
        name="post_sidecar_delete_nieg_host",
        method="POST",
        path="/api/v3/sidecar/delete/nieg/host",
    )

    # bkapi resource post_sidecar_findmany_company_host
    # post_sidecar_findmany_company_host
    post_sidecar_findmany_company_host = bind_property(
        Operation,
        name="post_sidecar_findmany_company_host",
        method="POST",
        path="/api/v3/sidecar/findmany/company/host",
    )

    # bkapi resource post_sidecar_import_nieg_host
    # post_sidecar_import_nieg_host
    post_sidecar_import_nieg_host = bind_property(
        Operation,
        name="post_sidecar_import_nieg_host",
        method="POST",
        path="/api/v3/sidecar/import/nieg/host",
    )

    # bkapi resource post_sidecar_itsm_create_ticket
    # post_sidecar_itsm_create_ticket
    post_sidecar_itsm_create_ticket = bind_property(
        Operation,
        name="post_sidecar_itsm_create_ticket",
        method="POST",
        path="/api/v3/sidecar/itsm/create_ticket",
    )

    # bkapi resource post_system_config_user_config_blueking_modify
    # post_system_config_user_config_blueking_modify
    post_system_config_user_config_blueking_modify = bind_property(
        Operation,
        name="post_system_config_user_config_blueking_modify",
        method="POST",
        path="/api/v3/system/config/user_config/blueking_modify",
    )

    # bkapi resource post_topo_delete_biz_extra_moudle
    # post_topo_delete_biz_extra_moudle
    post_topo_delete_biz_extra_moudle = bind_property(
        Operation,
        name="post_topo_delete_biz_extra_moudle",
        method="POST",
        path="/api/v3/topo/delete/biz/extra_moudle",
    )

    # bkapi resource post_topo_update_biz_idle_set
    # post_topo_update_biz_idle_set
    post_topo_update_biz_idle_set = bind_property(
        Operation,
        name="post_topo_update_biz_idle_set",
        method="POST",
        path="/api/v3/topo/update/biz/idle_set",
    )

    # bkapi resource post_update_field_template_bind_object
    # post_update_field_template_bind_object
    post_update_field_template_bind_object = bind_property(
        Operation,
        name="post_update_field_template_bind_object",
        method="POST",
        path="/api/v3/update/field_template/bind/object",
    )

    # bkapi resource post_update_field_template_unbind_object
    # post_update_field_template_unbind_object
    post_update_field_template_unbind_object = bind_property(
        Operation,
        name="post_update_field_template_unbind_object",
        method="POST",
        path="/api/v3/update/field_template/unbind/object",
    )

    # bkapi resource post_update_objectattr_index
    # post_update_objectattr_index
    post_update_objectattr_index = bind_property(
        Operation,
        name="post_update_objectattr_index",
        method="POST",
        path="/api/v3/update/objectattr/index/{bk_obj_id}/{propertyId}",
    )

    # bkapi resource post_update_objecttopo_scope_type_global_scope_id_0
    # post_update_objecttopo_scope_type_global_scope_id_0
    post_update_objecttopo_scope_type_global_scope_id_0 = bind_property(
        Operation,
        name="post_update_objecttopo_scope_type_global_scope_id_0",
        method="POST",
        path="/api/v3/update/objecttopo/scope_type/global/scope_id/0",
    )

    # bkapi resource post_update_operation_chart
    # post_update_operation_chart
    post_update_operation_chart = bind_property(
        Operation,
        name="post_update_operation_chart",
        method="POST",
        path="/api/v3/update/operation/chart",
    )

    # bkapi resource post_update_operation_chart_position
    # post_update_operation_chart_position
    post_update_operation_chart_position = bind_property(
        Operation,
        name="post_update_operation_chart_position",
        method="POST",
        path="/api/v3/update/operation/chart/position",
    )

    # bkapi resource post_update_topo_field_template_sync
    # post_update_topo_field_template_sync
    post_update_topo_field_template_sync = bind_property(
        Operation,
        name="post_update_topo_field_template_sync",
        method="POST",
        path="/api/v3/update/topo/field_template/sync",
    )

    # bkapi resource post_updatemany_proc_service_instance_labels
    # post_updatemany_proc_service_instance_labels
    post_updatemany_proc_service_instance_labels = bind_property(
        Operation,
        name="post_updatemany_proc_service_instance_labels",
        method="POST",
        path="/api/v3/updatemany/proc/service_instance/labels",
    )

    # bkapi resource post_updatemany_proc_service_template_host_apply_plan_run
    # post_updatemany_proc_service_template_host_apply_plan_run
    post_updatemany_proc_service_template_host_apply_plan_run = bind_property(
        Operation,
        name="post_updatemany_proc_service_template_host_apply_plan_run",
        method="POST",
        path="/api/v3/updatemany/proc/service_template/host_apply_plan/run",
    )

    # bkapi resource post_usercustom
    # post_usercustom
    post_usercustom = bind_property(
        Operation,
        name="post_usercustom",
        method="POST",
        path="/api/v3/usercustom",
    )

    # bkapi resource post_usercustom_default_model
    # post_usercustom_default_model
    post_usercustom_default_model = bind_property(
        Operation,
        name="post_usercustom_default_model",
        method="POST",
        path="/api/v3/usercustom/default/model",
    )

    # bkapi resource post_usercustom_default_model_sub
    # post_usercustom_default_model_sub
    post_usercustom_default_model_sub = bind_property(
        Operation,
        name="post_usercustom_default_model_sub",
        method="POST",
        path="/api/v3/usercustom/default/model/{bk_obj_id}",
    )

    # bkapi resource post_usercustom_default_search
    # post_usercustom_default_search
    post_usercustom_default_search = bind_property(
        Operation,
        name="post_usercustom_default_search",
        method="POST",
        path="/api/v3/usercustom/default/search",
    )

    # bkapi resource post_usercustom_user_search
    # post_usercustom_user_search
    post_usercustom_user_search = bind_property(
        Operation,
        name="post_usercustom_user_search",
        method="POST",
        path="/api/v3/usercustom/user/search",
    )

    # bkapi resource push_host_identifier
    # 推送主机身份
    push_host_identifier = bind_property(
        Operation,
        name="push_host_identifier",
        method="POST",
        path="/api/v3/event/push/host_identifier",
    )

    # bkapi resource put_biz_status_disabled
    # put_biz_status_disabled
    put_biz_status_disabled = bind_property(
        Operation,
        name="put_biz_status_disabled",
        method="PUT",
        path="/api/v3/biz/status/disabled/{bk_supplier_account}/{bk_biz_id}",
    )

    # bkapi resource put_biz_status_enable
    # put_biz_status_enable
    put_biz_status_enable = bind_property(
        Operation,
        name="put_biz_status_enable",
        method="PUT",
        path="/api/v3/biz/status/enable/{bk_supplier_account}/{bk_biz_id}",
    )

    # bkapi resource put_hosts_favorites
    # put_hosts_favorites
    put_hosts_favorites = bind_property(
        Operation,
        name="put_hosts_favorites",
        method="PUT",
        path="/api/v3/hosts/favorites/{id}",
    )

    # bkapi resource put_hosts_favorites__incr
    # put_hosts_favorites__incr
    put_hosts_favorites__incr = bind_property(
        Operation,
        name="put_hosts_favorites__incr",
        method="PUT",
        path="/api/v3/hosts/favorites/{id}/incr",
    )

    # bkapi resource put_module_host_apply_enable_status_bk_biz_id
    # put_module_host_apply_enable_status_bk_biz_id
    put_module_host_apply_enable_status_bk_biz_id = bind_property(
        Operation,
        name="put_module_host_apply_enable_status_bk_biz_id",
        method="PUT",
        path="/api/v3/module/host_apply_enable_status/bk_biz_id/{bk_biz_id}",
    )

    # bkapi resource put_update_associationtype
    # put_update_associationtype
    put_update_associationtype = bind_property(
        Operation,
        name="put_update_associationtype",
        method="PUT",
        path="/api/v3/update/associationtype/{id}",
    )

    # bkapi resource put_update_cloud_account
    # put_update_cloud_account
    put_update_cloud_account = bind_property(
        Operation,
        name="put_update_cloud_account",
        method="PUT",
        path="/api/v3/update/cloud/account/{id}",
    )

    # bkapi resource put_update_cloud_sync_task
    # put_update_cloud_sync_task
    put_update_cloud_sync_task = bind_property(
        Operation,
        name="put_update_cloud_sync_task",
        method="PUT",
        path="/api/v3/update/cloud/sync/task/{id}",
    )

    # bkapi resource put_update_field_template
    # put_update_field_template
    put_update_field_template = bind_property(
        Operation,
        name="put_update_field_template",
        method="PUT",
        path="/api/v3/update/field_template",
    )

    # bkapi resource put_update_field_template_info
    # put_update_field_template_info
    put_update_field_template_info = bind_property(
        Operation,
        name="put_update_field_template_info",
        method="PUT",
        path="/api/v3/update/field_template/info",
    )

    # bkapi resource put_update_objectassociation
    # put_update_objectassociation
    put_update_objectassociation = bind_property(
        Operation,
        name="put_update_objectassociation",
        method="PUT",
        path="/api/v3/update/objectassociation/{id}",
    )

    # bkapi resource put_update_objectattgroup
    # put_update_objectattgroup
    put_update_objectattgroup = bind_property(
        Operation,
        name="put_update_objectattgroup",
        method="PUT",
        path="/api/v3/update/objectattgroup",
    )

    # bkapi resource put_update_objectattgroup_groupindex
    # put_update_objectattgroup_groupindex
    put_update_objectattgroup_groupindex = bind_property(
        Operation,
        name="put_update_objectattgroup_groupindex",
        method="PUT",
        path="/api/v3/update/objectattgroup/groupindex",
    )

    # bkapi resource put_update_objectunique_object__unique
    # put_update_objectunique_object__unique
    put_update_objectunique_object__unique = bind_property(
        Operation,
        name="put_update_objectunique_object__unique",
        method="PUT",
        path="/api/v3/update/objectunique/object/{bk_obj_id}/unique/{id}",
    )

    # bkapi resource put_update_proc_process_instance_by_ids
    # put_update_proc_process_instance_by_ids
    put_update_proc_process_instance_by_ids = bind_property(
        Operation,
        name="put_update_proc_process_instance_by_ids",
        method="PUT",
        path="/api/v3/update/proc/process_instance/by_ids",
    )

    # bkapi resource put_update_proc_service_instance_sync
    # put_update_proc_service_instance_sync
    put_update_proc_service_instance_sync = bind_property(
        Operation,
        name="put_update_proc_service_instance_sync",
        method="PUT",
        path="/api/v3/update/proc/service_instance/sync",
    )

    # bkapi resource put_update_proc_service_template_all_info
    # put_update_proc_service_template_all_info
    put_update_proc_service_template_all_info = bind_property(
        Operation,
        name="put_update_proc_service_template_all_info",
        method="PUT",
        path="/api/v3/update/proc/service_template/all_info",
    )

    # bkapi resource put_update_proc_service_template_attribute
    # put_update_proc_service_template_attribute
    put_update_proc_service_template_attribute = bind_property(
        Operation,
        name="put_update_proc_service_template_attribute",
        method="PUT",
        path="/api/v3/update/proc/service_template/attribute",
    )

    # bkapi resource put_update_resource_directory
    # put_update_resource_directory
    put_update_resource_directory = bind_property(
        Operation,
        name="put_update_resource_directory",
        method="PUT",
        path="/api/v3/update/resource/directory/{id}",
    )

    # bkapi resource put_update_topo_set_template_all_info
    # put_update_topo_set_template_all_info
    put_update_topo_set_template_all_info = bind_property(
        Operation,
        name="put_update_topo_set_template_all_info",
        method="PUT",
        path="/api/v3/update/topo/set_template/all_info",
    )

    # bkapi resource put_update_topo_set_template_attribute
    # put_update_topo_set_template_attribute
    put_update_topo_set_template_attribute = bind_property(
        Operation,
        name="put_update_topo_set_template_attribute",
        method="PUT",
        path="/api/v3/update/topo/set_template/attribute",
    )

    # bkapi resource put_updatemany_proc_service_instance_biz
    # put_updatemany_proc_service_instance_biz
    put_updatemany_proc_service_instance_biz = bind_property(
        Operation,
        name="put_updatemany_proc_service_instance_biz",
        method="PUT",
        path="/api/v3/updatemany/proc/service_instance/biz/{bk_biz_id}",
    )

    # bkapi resource put_updatemany_proc_service_template_host_apply_enable_status_biz
    # put_updatemany_proc_service_template_host_apply_enable_status_biz
    put_updatemany_proc_service_template_host_apply_enable_status_biz = bind_property(
        Operation,
        name="put_updatemany_proc_service_template_host_apply_enable_status_biz",
        method="PUT",
        path="/api/v3/updatemany/proc/service_template/host_apply_enable_status/biz/{bk_biz_id}",
    )

    # bkapi resource read_instance
    # ReadInstance
    read_instance = bind_property(
        Operation,
        name="read_instance",
        method="POST",
        path="/api/v3/find/instance/{bk_obj_id}",
    )

    # bkapi resource read_model
    # ReadModel
    read_model = bind_property(
        Operation,
        name="read_model",
        method="POST",
        path="/api/v3/find/object/model",
    )

    # bkapi resource read_model_for_ui
    # ReadModelForUI
    read_model_for_ui = bind_property(
        Operation,
        name="read_model_for_ui",
        method="POST",
        path="/api/v3/find/object/model/web",
    )

    # bkapi resource read_module_association
    # ReadModuleAssociation
    read_module_association = bind_property(
        Operation,
        name="read_module_association",
        method="POST",
        path="/api/v3/find/instassociation/model",
    )

    # bkapi resource remove_label_from_service_instance
    # 从服务实例移除标签
    remove_label_from_service_instance = bind_property(
        Operation,
        name="remove_label_from_service_instance",
        method="DELETE",
        path="/api/v3/deletemany/proc/service_instance/labels",
    )

    # bkapi resource resource_watch
    # 监听资源变化事件
    resource_watch = bind_property(
        Operation,
        name="resource_watch",
        method="POST",
        path="/api/v3/event/watch/resource/{bk_resource}",
    )

    # bkapi resource search_biz_inst_topo
    # 查询业务实例拓扑
    search_biz_inst_topo = bind_property(
        Operation,
        name="search_biz_inst_topo",
        method="POST",
        path="/api/v3/find/topoinst/biz/{bk_biz_id}",
    )

    # bkapi resource search_business
    # 查询业务
    search_business = bind_property(
        Operation,
        name="search_business",
        method="POST",
        path="/api/v3/biz/search/{bk_supplier_account}",
    )

    # bkapi resource search_classifications
    # 查询模型分类
    search_classifications = bind_property(
        Operation,
        name="search_classifications",
        method="POST",
        path="/api/v3/find/objectclassification",
    )

    # bkapi resource search_cloud_area
    # 查询管控区域
    search_cloud_area = bind_property(
        Operation,
        name="search_cloud_area",
        method="POST",
        path="/api/v3/findmany/cloudarea",
    )

    # bkapi resource search_cmpy_business1
    # 查询公司cmdb的一级业务
    search_cmpy_business1 = bind_property(
        Operation,
        name="search_cmpy_business1",
        method="POST",
        path="/api/v3/sidecar/findmany/business1",
    )

    # bkapi resource search_cmpy_business2
    # 查询公司cmdb的二级业务
    search_cmpy_business2 = bind_property(
        Operation,
        name="search_cmpy_business2",
        method="POST",
        path="/api/v3/sidecar/findmany/business2",
    )

    # bkapi resource search_cmpy_business3
    # 查询公司cmdb的三级业务
    search_cmpy_business3 = bind_property(
        Operation,
        name="search_cmpy_business3",
        method="POST",
        path="/api/v3/sidecar/findmany/business3",
    )

    # bkapi resource search_cmpy_businessdept
    # 查询公司cmdb的部门
    search_cmpy_businessdept = bind_property(
        Operation,
        name="search_cmpy_businessdept",
        method="POST",
        path="/api/v3/sidecar/findmany/businessdept",
    )

    # bkapi resource search_cost_info_relation
    # 查询业务、obs产品和规划产品三者之间的关系
    search_cost_info_relation = bind_property(
        Operation,
        name="search_cost_info_relation",
        method="POST",
        path="/api/v3/sidecar/findmany/business/cost_info_relation",
    )

    # bkapi resource search_default_app
    # SearchDefaultApp
    search_default_app = bind_property(
        Operation,
        name="search_default_app",
        method="POST",
        path="/api/v3/biz/default/{bk_supplier_account}/search",
    )

    # bkapi resource search_dynamic_group
    # 搜索动态分组
    search_dynamic_group = bind_property(
        Operation,
        name="search_dynamic_group",
        method="POST",
        path="/api/v3/dynamicgroup/search/{bk_biz_id}",
    )

    # bkapi resource search_host_lock
    # 查询主机锁
    search_host_lock = bind_property(
        Operation,
        name="search_host_lock",
        method="POST",
        path="/api/v3/host/lock/search",
    )

    # bkapi resource search_hostidentifier
    # 根据条件查询主机身份
    search_hostidentifier = bind_property(
        Operation,
        name="search_hostidentifier",
        method="POST",
        path="/api/v3/identifier/host/search",
    )

    # bkapi resource search_inst
    # 根据关联关系实例查询模型实例
    search_inst = bind_property(
        Operation,
        name="search_inst",
        method="POST",
        path="/api/v3/find/instassociation/object/{bk_obj_id}",
    )

    # bkapi resource search_inst_association_topo
    # 查询实例关联拓扑
    search_inst_association_topo = bind_property(
        Operation,
        name="search_inst_association_topo",
        method="POST",
        path="/api/v3/find/insttopo/object/{bk_obj_id}/inst/{bk_inst_id}",
    )

    # bkapi resource search_inst_asst_object_inst_base_info
    # 查询实例关联模型实例基本信息
    search_inst_asst_object_inst_base_info = bind_property(
        Operation,
        name="search_inst_asst_object_inst_base_info",
        method="POST",
        path="/api/v3/findmany/inst/association/association_object/inst_base_info",
    )

    # bkapi resource search_inst_by_object
    # 查询实例详情
    search_inst_by_object = bind_property(
        Operation,
        name="search_inst_by_object",
        method="POST",
        path="/api/v3/inst/search/owner/{bk_supplier_account}/object/{bk_obj_id}",
    )

    # bkapi resource search_instance_associations
    # 查询模型实例关系
    search_instance_associations = bind_property(
        Operation,
        name="search_instance_associations",
        method="POST",
        path="/api/v3/search/instance_associations/object/{bk_obj_id}",
    )

    # bkapi resource search_module
    # 查询模块
    search_module = bind_property(
        Operation,
        name="search_module",
        method="POST",
        path="/api/v3/module/search/{bk_supplier_account}/{bk_biz_id}/{bk_set_id}",
    )

    # bkapi resource search_net_collect_device
    # SearchNetCollectDevice
    search_net_collect_device = bind_property(
        Operation,
        name="search_net_collect_device",
        method="POST",
        path="/api/v3/collector/netcollect/device/action/search",
    )

    # bkapi resource search_net_collect_device_batch
    # SearchNetCollectDeviceBatch
    search_net_collect_device_batch = bind_property(
        Operation,
        name="search_net_collect_device_batch",
        method="POST",
        path="/api/v3/collector/netcollect/device/action/batch",
    )

    # bkapi resource search_net_device_property
    # SearchNetDeviceProperty
    search_net_device_property = bind_property(
        Operation,
        name="search_net_device_property",
        method="POST",
        path="/api/v3/collector/netcollect/property/action/search",
    )

    # bkapi resource search_net_device_property_batch
    # SearchNetDevicePropertyBatch
    search_net_device_property_batch = bind_property(
        Operation,
        name="search_net_device_property_batch",
        method="POST",
        path="/api/v3/collector/netcollect/property/action/batch",
    )

    # bkapi resource search_object_attribute
    # 查询对象模型属性
    search_object_attribute = bind_property(
        Operation,
        name="search_object_attribute",
        method="POST",
        path="/api/v3/find/objectattr",
    )

    # bkapi resource search_object_instances
    # 查询模型实例
    search_object_instances = bind_property(
        Operation,
        name="search_object_instances",
        method="POST",
        path="/api/v3/search/instances/object/{bk_obj_id}",
    )

    # bkapi resource search_object_topo
    # 查询普通模型拓扑
    search_object_topo = bind_property(
        Operation,
        name="search_object_topo",
        method="POST",
        path="/api/v3/find/objecttopology",
    )

    # bkapi resource search_object_unique
    # SearchObjectUnique
    search_object_unique = bind_property(
        Operation,
        name="search_object_unique",
        method="POST",
        path="/api/v3/find/objectunique/object/{bk_obj_id}",
    )

    # bkapi resource search_object_with_total_info
    # SearchObjectWithTotalInfo
    search_object_with_total_info = bind_property(
        Operation,
        name="search_object_with_total_info",
        method="POST",
        path="/api/v3/findmany/object/total/info",
    )

    # bkapi resource search_objects
    # 查询模型
    search_objects = bind_property(
        Operation,
        name="search_objects",
        method="POST",
        path="/api/v3/find/object",
    )

    # bkapi resource search_platform_setting
    # SearchPlatformSetting
    search_platform_setting = bind_property(
        Operation,
        name="search_platform_setting",
        method="GET",
        path="/api/v3/admin/find/system_config/platform_setting/{type}",
    )

    # bkapi resource search_process_instances
    # 根据条件查询业务下的进程实例详情
    search_process_instances = bind_property(
        Operation,
        name="search_process_instances",
        method="POST",
        path="/api/v3/sidecar/findmany/proc/process_instance/detail/by_condition/biz/{bk_biz_id}",
    )

    # bkapi resource search_related_inst_asso
    # 查询某实例所有的关联关系（包含其作为关联关系原模型和关联关系目标模型的情况）
    search_related_inst_asso = bind_property(
        Operation,
        name="search_related_inst_asso",
        method="POST",
        path="/api/v3/find/instassociation/related",
    )

    # bkapi resource search_set
    # 查询集群
    search_set = bind_property(
        Operation,
        name="search_set",
        method="POST",
        path="/api/v3/set/search/{bk_supplier_account}/{bk_biz_id}",
    )

    # bkapi resource sync_host_info_from_cmpy
    # 同步公司cmdb主机详情信息到cc3.0
    sync_host_info_from_cmpy = bind_property(
        Operation,
        name="sync_host_info_from_cmpy",
        method="POST",
        path="/api/v3/shipper/sync/cmdb/sync_host_info_from_cmpy",
    )

    # bkapi resource sync_host_vip_info
    # 从tgw同步主机对应的vip、vport等信息
    sync_host_vip_info = bind_property(
        Operation,
        name="sync_host_vip_info",
        method="POST",
        path="/api/v3/tgw/sync_host_vip_info",
    )

    # bkapi resource sync_inst_id_rule
    # 同步刷新id规则字段值到该字段为空的模型实例
    sync_inst_id_rule = bind_property(
        Operation,
        name="sync_inst_id_rule",
        method="POST",
        path="/api/v3/sync/inst/id_rule",
    )

    # bkapi resource sync_set_template_to_set
    # 集群模板同步
    sync_set_template_to_set = bind_property(
        Operation,
        name="sync_set_template_to_set",
        method="POST",
        path="/api/v3/updatemany/topo/set_template/{set_template_id}/bk_biz_id/{bk_biz_id}/sync_to_instances",
    )

    # bkapi resource transfer_host_across_biz
    # 跨业务转移主机
    transfer_host_across_biz = bind_property(
        Operation,
        name="transfer_host_across_biz",
        method="POST",
        path="/api/v3/hosts/modules/across/biz",
    )

    # bkapi resource transfer_host_module
    # 业务内主机转移模块
    transfer_host_module = bind_property(
        Operation,
        name="transfer_host_module",
        method="POST",
        path="/api/v3/hosts/modules",
    )

    # bkapi resource transfer_host_to_another_biz
    # 主机交付与转移接口，该接口仅用于跨业务转移主机，不能进行同业务内主机转移。
    transfer_host_to_another_biz = bind_property(
        Operation,
        name="transfer_host_to_another_biz",
        method="POST",
        path="/api/v3/sidecar/host/transfer_host_to_another_biz",
    )

    # bkapi resource transfer_host_to_faultmodule
    # 上交主机到业务的故障机模块
    transfer_host_to_faultmodule = bind_property(
        Operation,
        name="transfer_host_to_faultmodule",
        method="POST",
        path="/api/v3/hosts/modules/fault",
    )

    # bkapi resource transfer_host_to_idlemodule
    # 上交主机到业务的空闲机模块
    transfer_host_to_idlemodule = bind_property(
        Operation,
        name="transfer_host_to_idlemodule",
        method="POST",
        path="/api/v3/hosts/modules/idle",
    )

    # bkapi resource transfer_host_to_recyclemodule
    # 上交主机到业务的待回收模块
    transfer_host_to_recyclemodule = bind_property(
        Operation,
        name="transfer_host_to_recyclemodule",
        method="POST",
        path="/api/v3/hosts/modules/recycle",
    )

    # bkapi resource transfer_host_to_resourcemodule
    # 上交主机至资源池
    transfer_host_to_resourcemodule = bind_property(
        Operation,
        name="transfer_host_to_resourcemodule",
        method="POST",
        path="/api/v3/hosts/modules/resource",
    )

    # bkapi resource transfer_resourcehost_to_idlemodule
    # 资源池主机分配至业务的空闲机模块
    transfer_resourcehost_to_idlemodule = bind_property(
        Operation,
        name="transfer_resourcehost_to_idlemodule",
        method="POST",
        path="/api/v3/hosts/modules/resource/idle",
    )

    # bkapi resource transfer_sethost_to_idle_module
    # 清空业务下集群/模块中主机
    transfer_sethost_to_idle_module = bind_property(
        Operation,
        name="transfer_sethost_to_idle_module",
        method="POST",
        path="/api/v3/hosts/modules/idle/set",
    )

    # bkapi resource unbind_host_agent
    # 将agent和主机解绑
    unbind_host_agent = bind_property(
        Operation,
        name="unbind_host_agent",
        method="POST",
        path="/api/v3/host/unbind/agent",
    )

    # bkapi resource update_biz_custom_field
    # 更新业务自定义模型属性
    update_biz_custom_field = bind_property(
        Operation,
        name="update_biz_custom_field",
        method="PUT",
        path="/api/v3/update/objectattr/biz/{bk_biz_id}/id/{id}",
    )

    # bkapi resource update_biz_property_batch
    # UpdateBizPropertyBatch
    update_biz_property_batch = bind_property(
        Operation,
        name="update_biz_property_batch",
        method="PUT",
        path="/api/v3/updatemany/biz/property",
    )

    # bkapi resource update_biz_sensitive
    # 更新业务敏感信息
    update_biz_sensitive = bind_property(
        Operation,
        name="update_biz_sensitive",
        method="PUT",
        path="/api/v3/sidecar/update/sensitive/biz/{bk_biz_id}",
    )

    # bkapi resource update_business
    # 修改业务
    update_business = bind_property(
        Operation,
        name="update_business",
        method="PUT",
        path="/api/v3/biz/{bk_supplier_account}/{bk_biz_id}",
    )

    # bkapi resource update_business_enable_status
    # 修改业务启用状态
    update_business_enable_status = bind_property(
        Operation,
        name="update_business_enable_status",
        method="PUT",
        path="/api/v3/biz/status/{flag}/{bk_supplier_account}/{bk_biz_id}",
    )

    # bkapi resource update_classification
    # 更新模型分类
    update_classification = bind_property(
        Operation,
        name="update_classification",
        method="PUT",
        path="/api/v3/update/objectclassification/{id}",
    )

    # bkapi resource update_cloud_area
    # 更新管控区域
    update_cloud_area = bind_property(
        Operation,
        name="update_cloud_area",
        method="PUT",
        path="/api/v3/update/cloudarea/{bk_cloud_id}",
    )

    # bkapi resource update_dynamic_group
    # 更新动态分组
    update_dynamic_group = bind_property(
        Operation,
        name="update_dynamic_group",
        method="PUT",
        path="/api/v3/dynamicgroup/{bk_biz_id}/{id}",
    )

    # bkapi resource update_full_sync_cond_for_cache
    # 更新全量同步缓存条件信息
    update_full_sync_cond_for_cache = bind_property(
        Operation,
        name="update_full_sync_cond_for_cache",
        method="PUT",
        path="/api/v3/cache/update/full/sync/cond",
    )

    # bkapi resource update_host
    # 更新主机属性
    update_host = bind_property(
        Operation,
        name="update_host",
        method="PUT",
        path="/api/v3/hosts/batch",
    )

    # bkapi resource update_host_cloud_area_field
    # 更新主机的管控区域字段
    update_host_cloud_area_field = bind_property(
        Operation,
        name="update_host_cloud_area_field",
        method="PUT",
        path="/api/v3/updatemany/hosts/cloudarea_field",
    )

    # bkapi resource update_id_rule_incr_id
    # 更新id规则自增id
    update_id_rule_incr_id = bind_property(
        Operation,
        name="update_id_rule_incr_id",
        method="PUT",
        path="/api/v3/update/id_rule/incr_id",
    )

    # bkapi resource update_import_host
    # UpdateHost
    update_import_host = bind_property(
        Operation,
        name="update_import_host",
        method="PUT",
        path="/api/v3/hosts/update",
    )

    # bkapi resource update_inst
    # 更新对象实例
    update_inst = bind_property(
        Operation,
        name="update_inst",
        method="PUT",
        path="/api/v3/update/instance/object/{bk_obj_id}/inst/{bk_inst_id}",
    )

    # bkapi resource update_kube_cluster_type
    # 更新容器集群类型
    update_kube_cluster_type = bind_property(
        Operation,
        name="update_kube_cluster_type",
        method="PUT",
        path="/api/v3/update/kube/cluster/type",
    )

    # bkapi resource update_module
    # 更新模块
    update_module = bind_property(
        Operation,
        name="update_module",
        method="PUT",
        path="/api/v3/module/{bk_biz_id}/{bk_set_id}/{bk_module_id}",
    )

    # bkapi resource update_object
    # 更新定义
    update_object = bind_property(
        Operation,
        name="update_object",
        method="PUT",
        path="/api/v3/update/object/{id}",
    )

    # bkapi resource update_object_attribute
    # 更新对象模型属性
    update_object_attribute = bind_property(
        Operation,
        name="update_object_attribute",
        method="PUT",
        path="/api/v3/update/objectattr/{id}",
    )

    # bkapi resource update_object_topo_graphics
    # 更新拓扑图
    update_object_topo_graphics = bind_property(
        Operation,
        name="update_object_topo_graphics",
        method="POST",
        path="/api/v3/objects/topographics/scope_type/{scope_type}/scope_id/{scope_id}/action/{action}",
    )

    # bkapi resource update_platform_setting
    # UpdatePlatformSetting
    update_platform_setting = bind_property(
        Operation,
        name="update_platform_setting",
        method="PUT",
        path="/api/v3/admin/update/system_config/platform_setting",
    )

    # bkapi resource update_proc_template
    # 更新进程模板
    update_proc_template = bind_property(
        Operation,
        name="update_proc_template",
        method="PUT",
        path="/api/v3/update/proc/proc_template",
    )

    # bkapi resource update_process_instance
    # 更新进程实例
    update_process_instance = bind_property(
        Operation,
        name="update_process_instance",
        method="PUT",
        path="/api/v3/update/proc/process_instance",
    )

    # bkapi resource update_project_id
    # 更新项目id
    update_project_id = bind_property(
        Operation,
        name="update_project_id",
        method="PUT",
        path="/api/v3/update/project/bk_project_id",
    )

    # bkapi resource update_reinstall_cmdb_cvm
    # 更新公司cmdb中的cvm信息（hcm主机重装专用）
    update_reinstall_cmdb_cvm = bind_property(
        Operation,
        name="update_reinstall_cmdb_cvm",
        method="PUT",
        path="/api/v3/shipper/update/reinstall/cmdb/cvm",
    )

    # bkapi resource update_service_category
    # 更新服务分类
    update_service_category = bind_property(
        Operation,
        name="update_service_category",
        method="PUT",
        path="/api/v3/update/proc/service_category",
    )

    # bkapi resource update_service_template
    # 更新服务模板
    update_service_template = bind_property(
        Operation,
        name="update_service_template",
        method="PUT",
        path="/api/v3/update/proc/service_template",
    )

    # bkapi resource update_set
    # 更新集群
    update_set = bind_property(
        Operation,
        name="update_set",
        method="PUT",
        path="/api/v3/set/{bk_biz_id}/{bk_set_id}",
    )

    # bkapi resource update_set_template
    # 编辑集群模板
    update_set_template = bind_property(
        Operation,
        name="update_set_template",
        method="PUT",
        path="/api/v3/update/topo/set_template/{set_template_id}/bk_biz_id/{bk_biz_id}",
    )

    # bkapi resource update_special_biz_host
    # 更新特殊业务的主机信息，同步到公司cmdb
    update_special_biz_host = bind_property(
        Operation,
        name="update_special_biz_host",
        method="PUT",
        path="/api/v3/shipper/update/special/biz/host",
    )


class Client(APIGatewayClient):
    """Bkapi bk_cmdb client"""

    _api_name = "bk-cmdb"

    api = bind_property(Group, name="api")

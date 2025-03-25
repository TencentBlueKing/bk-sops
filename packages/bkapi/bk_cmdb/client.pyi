# -*- coding: utf-8 -*-
from bkapi_client_core.apigateway import APIGatewayClient, Operation, OperationGroup

class Group(OperationGroup):
    @property
    def abort_transaction(self) -> Operation:
        """
        bkapi resource abort_transaction
        AbortTransaction
        """
    @property
    def add_cloud_host_to_biz(self) -> Operation:
        """
        bkapi resource add_cloud_host_to_biz
        新增云主机到业务的空闲机模块
        """
    @property
    def add_default_app(self) -> Operation:
        """
        bkapi resource add_default_app
        AddDefaultApp
        """
    @property
    def add_host_by_excel(self) -> Operation:
        """
        bkapi resource add_host_by_excel
        AddHostByExcel
        """
    @property
    def add_host_from_cmpy(self) -> Operation:
        """
        bkapi resource add_host_from_cmpy
        同步公司cmdb新增主机到cc3.0
        """
    @property
    def add_host_lock(self) -> Operation:
        """
        bkapi resource add_host_lock
        新加主机锁
        """
    @property
    def add_host_to_business_idle(self) -> Operation:
        """
        bkapi resource add_host_to_business_idle
        添加主机到业务空闲机
        """
    @property
    def add_host_to_ci_biz(self) -> Operation:
        """
        bkapi resource add_host_to_ci_biz
        将主机导入到“蓝盾测试机”业务下
        """
    @property
    def add_host_to_resource(self) -> Operation:
        """
        bkapi resource add_host_to_resource
        新增主机到资源池
        """
    @property
    def add_host_to_resource_pool(self) -> Operation:
        """
        bkapi resource add_host_to_resource_pool
        添加主机到资源池
        """
    @property
    def add_inst_by_import(self) -> Operation:
        """
        bkapi resource add_inst_by_import
        AddInstByImport
        """
    @property
    def add_instance_association(self) -> Operation:
        """
        bkapi resource add_instance_association
        新建模型实例之间的关联关系
        """
    @property
    def add_label_for_service_instance(self) -> Operation:
        """
        bkapi resource add_label_for_service_instance
        为服务实例添加标签
        """
    @property
    def add_object_batch(self) -> Operation:
        """
        bkapi resource add_object_batch
        AddObjectBatch
        """
    @property
    def batch_create_inst(self) -> Operation:
        """
        bkapi resource batch_create_inst
        批量创建通用模型实例
        """
    @property
    def batch_create_instance_association(self) -> Operation:
        """
        bkapi resource batch_create_instance_association
        批量创建模型实例关联关系
        """
    @property
    def batch_create_kube_namespace(self) -> Operation:
        """
        bkapi resource batch_create_kube_namespace
        批量创建namespace
        """
    @property
    def batch_create_kube_node(self) -> Operation:
        """
        bkapi resource batch_create_kube_node
        批量创建容器节点
        """
    @property
    def batch_create_kube_pod(self) -> Operation:
        """
        bkapi resource batch_create_kube_pod
        批量创建容器pod
        """
    @property
    def batch_create_kube_workload(self) -> Operation:
        """
        bkapi resource batch_create_kube_workload
        批量创建workload
        """
    @property
    def batch_create_module(self) -> Operation:
        """
        bkapi resource batch_create_module
        批量创建模块
        """
    @property
    def batch_create_proc_template(self) -> Operation:
        """
        bkapi resource batch_create_proc_template
        批量创建进程模板
        """
    @property
    def batch_create_project(self) -> Operation:
        """
        bkapi resource batch_create_project
        批量创建项目
        """
    @property
    def batch_create_quoted_inst(self) -> Operation:
        """
        bkapi resource batch_create_quoted_inst
        批量创建被引用的模型的实例
        """
    @property
    def batch_delete_business_set(self) -> Operation:
        """
        bkapi resource batch_delete_business_set
        批量删除业务集
        """
    @property
    def batch_delete_inst(self) -> Operation:
        """
        bkapi resource batch_delete_inst
        批量删除实例
        """
    @property
    def batch_delete_kube_cluster(self) -> Operation:
        """
        bkapi resource batch_delete_kube_cluster
        批量删除容器集群
        """
    @property
    def batch_delete_kube_namespace(self) -> Operation:
        """
        bkapi resource batch_delete_kube_namespace
        批量删除namespace
        """
    @property
    def batch_delete_kube_node(self) -> Operation:
        """
        bkapi resource batch_delete_kube_node
        批量删除容器节点
        """
    @property
    def batch_delete_kube_pod(self) -> Operation:
        """
        bkapi resource batch_delete_kube_pod
        批量删除Pod
        """
    @property
    def batch_delete_kube_workload(self) -> Operation:
        """
        bkapi resource batch_delete_kube_workload
        批量删除workload
        """
    @property
    def batch_delete_project(self) -> Operation:
        """
        bkapi resource batch_delete_project
        批量删除项目
        """
    @property
    def batch_delete_quoted_inst(self) -> Operation:
        """
        bkapi resource batch_delete_quoted_inst
        批量删除被引用的模型的实例
        """
    @property
    def batch_delete_set(self) -> Operation:
        """
        bkapi resource batch_delete_set
        批量删除集群
        """
    @property
    def batch_update_business_set(self) -> Operation:
        """
        bkapi resource batch_update_business_set
        批量更新业务集信息
        """
    @property
    def batch_update_host(self) -> Operation:
        """
        bkapi resource batch_update_host
        批量更新主机属性
        """
    @property
    def batch_update_host_all_properties(self) -> Operation:
        """
        bkapi resource batch_update_host_all_properties
        根据主机id和属性批量更新主机属性
        """
    @property
    def batch_update_inst(self) -> Operation:
        """
        bkapi resource batch_update_inst
        批量更新对象实例
        """
    @property
    def batch_update_kube_cluster(self) -> Operation:
        """
        bkapi resource batch_update_kube_cluster
        批量更新容器集群信息
        """
    @property
    def batch_update_kube_namespace(self) -> Operation:
        """
        bkapi resource batch_update_kube_namespace
        批量更新namespace
        """
    @property
    def batch_update_kube_node(self) -> Operation:
        """
        bkapi resource batch_update_kube_node
        批量更新容器节点信息
        """
    @property
    def batch_update_kube_workload(self) -> Operation:
        """
        bkapi resource batch_update_kube_workload
        批量更新workload
        """
    @property
    def batch_update_project(self) -> Operation:
        """
        bkapi resource batch_update_project
        批量更新项目
        """
    @property
    def batch_update_quoted_inst(self) -> Operation:
        """
        bkapi resource batch_update_quoted_inst
        批量更新被引用的模型的实例
        """
    @property
    def bind_host_agent(self) -> Operation:
        """
        bkapi resource bind_host_agent
        将agent绑定到主机上
        """
    @property
    def check_objectattr_host_apply_enabled(self) -> Operation:
        """
        bkapi resource check_objectattr_host_apply_enabled
        check_objectattr_host_apply_enabled
        """
    @property
    def clone_host_property(self) -> Operation:
        """
        bkapi resource clone_host_property
        克隆主机属性
        """
    @property
    def clone_host_service_instance_proc(self) -> Operation:
        """
        bkapi resource clone_host_service_instance_proc
        克隆主机服务实例下的进程信息到新的主机服务实例中
        """
    @property
    def commit_transaction(self) -> Operation:
        """
        bkapi resource commit_transaction
        CommitTransaction
        """
    @property
    def count_biz_host_cpu(self) -> Operation:
        """
        bkapi resource count_biz_host_cpu
        统计每个业务下主机CPU数量（成本管理专用接口）
        """
    @property
    def count_instance_associations(self) -> Operation:
        """
        bkapi resource count_instance_associations
        查询模型实例关系数量
        """
    @property
    def count_object_instances(self) -> Operation:
        """
        bkapi resource count_object_instances
        查询模型实例数量
        """
    @property
    def count_object_instances_by_filters(self) -> Operation:
        """
        bkapi resource count_object_instances_by_filters
        count_object_instances_by_filters
        """
    @property
    def create_biz_custom_field(self) -> Operation:
        """
        bkapi resource create_biz_custom_field
        创建业务自定义模型属性
        """
    @property
    def create_business(self) -> Operation:
        """
        bkapi resource create_business
        新建业务
        """
    @property
    def create_business_set(self) -> Operation:
        """
        bkapi resource create_business_set
        创建业务集
        """
    @property
    def create_classification(self) -> Operation:
        """
        bkapi resource create_classification
        添加模型分类
        """
    @property
    def create_cloud_area(self) -> Operation:
        """
        bkapi resource create_cloud_area
        创建管控区域
        """
    @property
    def create_dynamic_group(self) -> Operation:
        """
        bkapi resource create_dynamic_group
        创建动态分组
        """
    @property
    def create_full_sync_cond_for_cache(self) -> Operation:
        """
        bkapi resource create_full_sync_cond_for_cache
        创建全量同步缓存条件
        """
    @property
    def create_inst(self) -> Operation:
        """
        bkapi resource create_inst
        创建实例
        """
    @property
    def create_kube_cluster(self) -> Operation:
        """
        bkapi resource create_kube_cluster
        创建容器集群
        """
    @property
    def create_many_object(self) -> Operation:
        """
        bkapi resource create_many_object
        CreateManyObject
        """
    @property
    def create_module(self) -> Operation:
        """
        bkapi resource create_module
        创建模块
        """
    @property
    def create_object(self) -> Operation:
        """
        bkapi resource create_object
        创建模型
        """
    @property
    def create_object_attribute(self) -> Operation:
        """
        bkapi resource create_object_attribute
        创建模型属性
        """
    @property
    def create_process_instance(self) -> Operation:
        """
        bkapi resource create_process_instance
        创建进程实例
        """
    @property
    def create_service_category(self) -> Operation:
        """
        bkapi resource create_service_category
        新建服务分类
        """
    @property
    def create_service_instance(self) -> Operation:
        """
        bkapi resource create_service_instance
        创建服务实例
        """
    @property
    def create_service_template(self) -> Operation:
        """
        bkapi resource create_service_template
        新建服务模板
        """
    @property
    def create_set(self) -> Operation:
        """
        bkapi resource create_set
        创建集群
        """
    @property
    def create_set_template(self) -> Operation:
        """
        bkapi resource create_set_template
        新建集群模板
        """
    @property
    def delete_biz(self) -> Operation:
        """
        bkapi resource delete_biz
        DeleteBiz
        """
    @property
    def delete_classification(self) -> Operation:
        """
        bkapi resource delete_classification
        删除模型分类
        """
    @property
    def delete_cloud_area(self) -> Operation:
        """
        bkapi resource delete_cloud_area
        删除管控区域
        """
    @property
    def delete_cloud_host_from_biz(self) -> Operation:
        """
        bkapi resource delete_cloud_host_from_biz
        从业务空闲机集群删除云主机
        """
    @property
    def delete_delete_associationtype(self) -> Operation:
        """
        bkapi resource delete_delete_associationtype
        delete_delete_associationtype
        """
    @property
    def delete_delete_cloud_account(self) -> Operation:
        """
        bkapi resource delete_delete_cloud_account
        delete_delete_cloud_account
        """
    @property
    def delete_delete_cloud_sync_task(self) -> Operation:
        """
        bkapi resource delete_delete_cloud_sync_task
        delete_delete_cloud_sync_task
        """
    @property
    def delete_delete_field_template(self) -> Operation:
        """
        bkapi resource delete_delete_field_template
        delete_delete_field_template
        """
    @property
    def delete_delete_objectassociation(self) -> Operation:
        """
        bkapi resource delete_delete_objectassociation
        delete_delete_objectassociation
        """
    @property
    def delete_delete_objectattgroup(self) -> Operation:
        """
        bkapi resource delete_delete_objectattgroup
        delete_delete_objectattgroup
        """
    @property
    def delete_delete_operation_chart(self) -> Operation:
        """
        bkapi resource delete_delete_operation_chart
        delete_delete_operation_chart
        """
    @property
    def delete_delete_proc_service_template_attribute(self) -> Operation:
        """
        bkapi resource delete_delete_proc_service_template_attribute
        delete_delete_proc_service_template_attribute
        """
    @property
    def delete_delete_resource_directory(self) -> Operation:
        """
        bkapi resource delete_delete_resource_directory
        delete_delete_resource_directory
        """
    @property
    def delete_delete_topo_set_template_attribute(self) -> Operation:
        """
        bkapi resource delete_delete_topo_set_template_attribute
        delete_delete_topo_set_template_attribute
        """
    @property
    def delete_delete_topomodelmainline_object(self) -> Operation:
        """
        bkapi resource delete_delete_topomodelmainline_object
        delete_delete_topomodelmainline_object
        """
    @property
    def delete_deletemany_proc_service_template_host_apply_rule_biz(self) -> Operation:
        """
        bkapi resource delete_deletemany_proc_service_template_host_apply_rule_biz
        delete_deletemany_proc_service_template_host_apply_rule_biz
        """
    @property
    def delete_dynamic_group(self) -> Operation:
        """
        bkapi resource delete_dynamic_group
        删除动态分组
        """
    @property
    def delete_full_sync_cond_for_cache(self) -> Operation:
        """
        bkapi resource delete_full_sync_cond_for_cache
        删除全量同步缓存条件
        """
    @property
    def delete_host(self) -> Operation:
        """
        bkapi resource delete_host
        删除主机
        """
    @property
    def delete_host_deletemany_module_host_apply_rule_bk_biz_id(self) -> Operation:
        """
        bkapi resource delete_host_deletemany_module_host_apply_rule_bk_biz_id
        delete_host_deletemany_module_host_apply_rule_bk_biz_id
        """
    @property
    def delete_host_from_ci_biz(self) -> Operation:
        """
        bkapi resource delete_host_from_ci_biz
        删除(移出)“蓝盾测试机”业务下的主机
        """
    @property
    def delete_host_lock(self) -> Operation:
        """
        bkapi resource delete_host_lock
        删除主机锁
        """
    @property
    def delete_hosts_favorites(self) -> Operation:
        """
        bkapi resource delete_hosts_favorites
        delete_hosts_favorites
        """
    @property
    def delete_inst(self) -> Operation:
        """
        bkapi resource delete_inst
        删除实例
        """
    @property
    def delete_instance_association(self) -> Operation:
        """
        bkapi resource delete_instance_association
        删除模型实例之间的关联关系
        """
    @property
    def delete_module(self) -> Operation:
        """
        bkapi resource delete_module
        删除模块
        """
    @property
    def delete_object(self) -> Operation:
        """
        bkapi resource delete_object
        删除模型
        """
    @property
    def delete_object_attribute(self) -> Operation:
        """
        bkapi resource delete_object_attribute
        删除对象模型属性
        """
    @property
    def delete_proc_template(self) -> Operation:
        """
        bkapi resource delete_proc_template
        删除进程模板
        """
    @property
    def delete_process_instance(self) -> Operation:
        """
        bkapi resource delete_process_instance
        删除进程实例
        """
    @property
    def delete_related_inst_asso(self) -> Operation:
        """
        bkapi resource delete_related_inst_asso
        删除某实例所有的关联关系（包含其作为关联关系原模型和关联关系目标模型的情况）
        """
    @property
    def delete_service_category(self) -> Operation:
        """
        bkapi resource delete_service_category
        删除服务分类
        """
    @property
    def delete_service_instance(self) -> Operation:
        """
        bkapi resource delete_service_instance
        删除服务实例
        """
    @property
    def delete_service_template(self) -> Operation:
        """
        bkapi resource delete_service_template
        删除服务模板
        """
    @property
    def delete_set(self) -> Operation:
        """
        bkapi resource delete_set
        删除集群
        """
    @property
    def delete_set_template(self) -> Operation:
        """
        bkapi resource delete_set_template
        删除集群模板
        """
    @property
    def execute_dynamic_group(self) -> Operation:
        """
        bkapi resource execute_dynamic_group
        执行动态分组
        """
    @property
    def find_association_by_object_association_i_d(self) -> Operation:
        """
        bkapi resource find_association_by_object_association_i_d
        FindAssociationByObjectAssociationID
        """
    @property
    def find_audit_by_id(self) -> Operation:
        """
        bkapi resource find_audit_by_id
        根据审计ID获取详细信息
        """
    @property
    def find_biz_sensitive_batch(self) -> Operation:
        """
        bkapi resource find_biz_sensitive_batch
        批量查询业务敏感信息
        """
    @property
    def find_biz_tree_brief_info(self) -> Operation:
        """
        bkapi resource find_biz_tree_brief_info
        查询业务topo树的简要信息, 只包含集群、模块和主机
        """
    @property
    def find_brief_biz_topo_node_relation(self) -> Operation:
        """
        bkapi resource find_brief_biz_topo_node_relation
        查询业务主线实例拓扑源与目标节点的关系信息
        """
    @property
    def find_host_biz_relations(self) -> Operation:
        """
        bkapi resource find_host_biz_relations
        查询主机业务关系信息
        """
    @property
    def find_host_by_service_template(self) -> Operation:
        """
        bkapi resource find_host_by_service_template
        查询服务模板下的主机
        """
    @property
    def find_host_by_set_template(self) -> Operation:
        """
        bkapi resource find_host_by_set_template
        查询集群模板下的主机
        """
    @property
    def find_host_by_topo(self) -> Operation:
        """
        bkapi resource find_host_by_topo
        查询拓扑节点下的主机
        """
    @property
    def find_host_identifier_push_result(self) -> Operation:
        """
        bkapi resource find_host_identifier_push_result
        获取推送主机身份任务结果
        """
    @property
    def find_host_relations_with_topo(self) -> Operation:
        """
        bkapi resource find_host_relations_with_topo
        根据业务拓扑中的实例节点查询其下的主机关系信息
        """
    @property
    def find_host_topo_relation(self) -> Operation:
        """
        bkapi resource find_host_topo_relation
        获取主机与拓扑的关系
        """
    @property
    def find_host_typeclass_relation(self) -> Operation:
        """
        bkapi resource find_host_typeclass_relation
        查询公司cmdb服务器设备型号和类型对应关系
        """
    @property
    def find_inst_id_rule_task_status(self) -> Operation:
        """
        bkapi resource find_inst_id_rule_task_status
        查询同步实例id规则字段状态
        """
    @property
    def find_instance_association(self) -> Operation:
        """
        bkapi resource find_instance_association
        查询模型实例之间的关联关系
        """
    @property
    def find_instassociation_with_inst(self) -> Operation:
        """
        bkapi resource find_instassociation_with_inst
        查询模型实例的关联关系及可选返回原模型或目标模型的实例详情
        """
    @property
    def find_module_batch(self) -> Operation:
        """
        bkapi resource find_module_batch
        批量查询某业务的模块详情
        """
    @property
    def find_module_host_relation(self) -> Operation:
        """
        bkapi resource find_module_host_relation
        根据模块ID查询主机和模块的关系
        """
    @property
    def find_module_with_relation(self) -> Operation:
        """
        bkapi resource find_module_with_relation
        根据条件查询业务下的模块
        """
    @property
    def find_object_association(self) -> Operation:
        """
        bkapi resource find_object_association
        查询模型之间的关联关系
        """
    @property
    def find_set_batch(self) -> Operation:
        """
        bkapi resource find_set_batch
        批量查询某业务的集群详情
        """
    @property
    def find_topo_node_paths(self) -> Operation:
        """
        bkapi resource find_topo_node_paths
        查询业务拓扑节点的拓扑路径
        """
    @property
    def get_biz_brief_cache_topo(self) -> Operation:
        """
        bkapi resource get_biz_brief_cache_topo
        查询业务的简要拓扑树信息，包含所有层级的数据，不包含主机
        """
    @property
    def get_biz_internal_module(self) -> Operation:
        """
        bkapi resource get_biz_internal_module
        查询业务的空闲机/故障机/待回收模块
        """
    @property
    def get_biz_kube_cache_topo(self) -> Operation:
        """
        bkapi resource get_biz_kube_cache_topo
        查询业务的容器拓扑树缓存信息，包含业务、Cluster、Namespace、Workload层级的数据
        """
    @property
    def get_biz_location(self) -> Operation:
        """
        bkapi resource get_biz_location
        查询业务在cc1.0还是在cc3.0
        """
    @property
    def get_biz_simplify(self) -> Operation:
        """
        bkapi resource get_biz_simplify
        get_biz_simplify
        """
    @property
    def get_biz_with_reduced(self) -> Operation:
        """
        bkapi resource get_biz_with_reduced
        get_biz_with_reduced
        """
    @property
    def get_dynamic_group(self) -> Operation:
        """
        bkapi resource get_dynamic_group
        查询指定动态分组
        """
    @property
    def get_find_audit_dict(self) -> Operation:
        """
        bkapi resource get_find_audit_dict
        get_find_audit_dict
        """
    @property
    def get_find_field_template(self) -> Operation:
        """
        bkapi resource get_find_field_template
        get_find_field_template
        """
    @property
    def get_find_kube__attributes(self) -> Operation:
        """
        bkapi resource get_find_kube__attributes
        get_find_kube__attributes
        """
    @property
    def get_find_proc_service_template__detail(self) -> Operation:
        """
        bkapi resource get_find_proc_service_template__detail
        get_find_proc_service_template__detail
        """
    @property
    def get_find_topo_set_template__bk_biz_id(self) -> Operation:
        """
        bkapi resource get_find_topo_set_template__bk_biz_id
        get_find_topo_set_template__bk_biz_id
        """
    @property
    def get_findmany_biz_set_simplify(self) -> Operation:
        """
        bkapi resource get_findmany_biz_set_simplify
        get_findmany_biz_set_simplify
        """
    @property
    def get_findmany_biz_set_with_reduced(self) -> Operation:
        """
        bkapi resource get_findmany_biz_set_with_reduced
        get_findmany_biz_set_with_reduced
        """
    @property
    def get_findmany_operation_chart(self) -> Operation:
        """
        bkapi resource get_findmany_operation_chart
        get_findmany_operation_chart
        """
    @property
    def get_host_base_info(self) -> Operation:
        """
        bkapi resource get_host_base_info
        获取主机详情
        """
    @property
    def get_host_data(self) -> Operation:
        """
        bkapi resource get_host_data
        GetHostData
        """
    @property
    def get_host_location(self) -> Operation:
        """
        bkapi resource get_host_location
        根据主机IP及云区域ID查询该主机所属业务是在cc1.0还是在cc3.0
        """
    @property
    def get_inst_detail(self) -> Operation:
        """
        bkapi resource get_inst_detail
        GetInstDetail
        """
    @property
    def get_inst_unique_fields(self) -> Operation:
        """
        bkapi resource get_inst_unique_fields
        GetInstUniqueFields
        """
    @property
    def get_mainline_object_topo(self) -> Operation:
        """
        bkapi resource get_mainline_object_topo
        查询主线模型的业务拓扑
        """
    @property
    def get_object_attr_with_table(self) -> Operation:
        """
        bkapi resource get_object_attr_with_table
        GetObjectAttrWithTable
        """
    @property
    def get_object_data(self) -> Operation:
        """
        bkapi resource get_object_data
        GetObjectData
        """
    @property
    def get_object_group(self) -> Operation:
        """
        bkapi resource get_object_group
        GetObjectGroup
        """
    @property
    def get_proc_template(self) -> Operation:
        """
        bkapi resource get_proc_template
        获取进程模板
        """
    @property
    def get_service_template(self) -> Operation:
        """
        bkapi resource get_service_template
        获取服务模板
        """
    @property
    def get_topo_internal___with_statistics(self) -> Operation:
        """
        bkapi resource get_topo_internal___with_statistics
        get_topo_internal___with_statistics
        """
    @property
    def group_related_resource_by_ids(self) -> Operation:
        """
        bkapi resource group_related_resource_by_ids
        group_related_resource_by_ids
        """
    @property
    def health_check(self) -> Operation:
        """
        bkapi resource health_check
        HealthCheck
        """
    @property
    def host_install_bk(self) -> Operation:
        """
        bkapi resource host_install_bk
        机器新加到蓝鲸业务拓扑中
        """
    @property
    def hosts_cr_transit_to_idle(self) -> Operation:
        """
        bkapi resource hosts_cr_transit_to_idle
        将主机从业务的资源中转模块转移到空闲机模块
        """
    @property
    def hosts_to_cr_transit(self) -> Operation:
        """
        bkapi resource hosts_to_cr_transit
        将主机转移到指定业务的资源中转模块
        """
    @property
    def import_association(self) -> Operation:
        """
        bkapi resource import_association
        ImportAssociation
        """
    @property
    def list_biz_hosts(self) -> Operation:
        """
        bkapi resource list_biz_hosts
        查询业务下的主机
        """
    @property
    def list_biz_hosts_topo(self) -> Operation:
        """
        bkapi resource list_biz_hosts_topo
        查询业务下的主机和拓扑信息
        """
    @property
    def list_business_in_business_set(self) -> Operation:
        """
        bkapi resource list_business_in_business_set
        查询业务集中的业务列表
        """
    @property
    def list_business_set(self) -> Operation:
        """
        bkapi resource list_business_set
        查询业务集
        """
    @property
    def list_business_set_topo(self) -> Operation:
        """
        bkapi resource list_business_set_topo
        查询业务集拓扑
        """
    @property
    def list_cached_kube_pod_label_key(self) -> Operation:
        """
        bkapi resource list_cached_kube_pod_label_key
        获取缓存的Pod的标签键列表
        """
    @property
    def list_cached_kube_pod_label_value(self) -> Operation:
        """
        bkapi resource list_cached_kube_pod_label_value
        获取缓存的Pod的标签键对应的值列表
        """
    @property
    def list_cached_res_by_full_sync_cond(self) -> Operation:
        """
        bkapi resource list_cached_res_by_full_sync_cond
        根据全量同步缓存条件拉取缓存的资源详情
        """
    @property
    def list_cached_resource_by_ids(self) -> Operation:
        """
        bkapi resource list_cached_resource_by_ids
        根据ID列表拉取缓存的资源详情
        """
    @property
    def list_field_template(self) -> Operation:
        """
        bkapi resource list_field_template
        ListFieldTemplate
        """
    @property
    def list_field_template_attr(self) -> Operation:
        """
        bkapi resource list_field_template_attr
        ListFieldTemplateAttr
        """
    @property
    def list_full_sync_cond_for_cache(self) -> Operation:
        """
        bkapi resource list_full_sync_cond_for_cache
        查询全量同步缓存条件
        """
    @property
    def list_host_detail_topology(self) -> Operation:
        """
        bkapi resource list_host_detail_topology
        根据主机条件信息查询主机详情及其所属的拓扑信息
        """
    @property
    def list_host_related_info(self) -> Operation:
        """
        bkapi resource list_host_related_info
        根据主机查询与主机相关的业务及自身详情信息
        """
    @property
    def list_host_service_template_id(self) -> Operation:
        """
        bkapi resource list_host_service_template_id
        查询主机所属的服务模版id列表信息
        """
    @property
    def list_host_total_mainline_topo(self) -> Operation:
        """
        bkapi resource list_host_total_mainline_topo
        查询主机及其对应topo
        """
    @property
    def list_hosts_without_biz(self) -> Operation:
        """
        bkapi resource list_hosts_without_biz
        没有业务ID的主机查询
        """
    @property
    def list_kube_cluster(self) -> Operation:
        """
        bkapi resource list_kube_cluster
        查询容器集群
        """
    @property
    def list_kube_container(self) -> Operation:
        """
        bkapi resource list_kube_container
        查询Container列表
        """
    @property
    def list_kube_container_by_topo(self) -> Operation:
        """
        bkapi resource list_kube_container_by_topo
        根据容器拓扑获取container信息
        """
    @property
    def list_kube_container_for_sec(self) -> Operation:
        """
        bkapi resource list_kube_container_for_sec
        查询Container列表(安全专用，后续删除)
        """
    @property
    def list_kube_namespace(self) -> Operation:
        """
        bkapi resource list_kube_namespace
        查询namespace
        """
    @property
    def list_kube_node(self) -> Operation:
        """
        bkapi resource list_kube_node
        查询容器节点
        """
    @property
    def list_kube_pod(self) -> Operation:
        """
        bkapi resource list_kube_pod
        查询Pod列表
        """
    @property
    def list_kube_pod_for_sec(self) -> Operation:
        """
        bkapi resource list_kube_pod_for_sec
        查询Pod列表(安全专用，后续删除)
        """
    @property
    def list_kube_workload(self) -> Operation:
        """
        bkapi resource list_kube_workload
        查询workload
        """
    @property
    def list_obj_field_tmpl_rel(self) -> Operation:
        """
        bkapi resource list_obj_field_tmpl_rel
        ListObjFieldTmplRel
        """
    @property
    def list_operation_audit(self) -> Operation:
        """
        bkapi resource list_operation_audit
        根据条件获取操作审计日志
        """
    @property
    def list_proc_template(self) -> Operation:
        """
        bkapi resource list_proc_template
        查询进程模板列表
        """
    @property
    def list_process_detail_by_ids(self) -> Operation:
        """
        bkapi resource list_process_detail_by_ids
        查询某业务下进程ID对应的进程详情
        """
    @property
    def list_process_instance(self) -> Operation:
        """
        bkapi resource list_process_instance
        查询进程实例列表
        """
    @property
    def list_process_related_info(self) -> Operation:
        """
        bkapi resource list_process_related_info
        点分五位查询进程实例相关信息
        """
    @property
    def list_process_with_vip_info(self) -> Operation:
        """
        bkapi resource list_process_with_vip_info
        查询带进程VIP信息的进程实例列表
        """
    @property
    def list_project(self) -> Operation:
        """
        bkapi resource list_project
        查询项目
        """
    @property
    def list_quoted_inst(self) -> Operation:
        """
        bkapi resource list_quoted_inst
        查询被引用的模型的实例列表
        """
    @property
    def list_resource_pool_hosts(self) -> Operation:
        """
        bkapi resource list_resource_pool_hosts
        查询资源池中的主机
        """
    @property
    def list_service_category(self) -> Operation:
        """
        bkapi resource list_service_category
        查询服务分类列表
        """
    @property
    def list_service_instance(self) -> Operation:
        """
        bkapi resource list_service_instance
        查询服务实例列表
        """
    @property
    def list_service_instance_by_host(self) -> Operation:
        """
        bkapi resource list_service_instance_by_host
        通过主机查询关联的服务实例列表
        """
    @property
    def list_service_instance_by_set_template(self) -> Operation:
        """
        bkapi resource list_service_instance_by_set_template
        通过集群模版查询关联的服务实例列表
        """
    @property
    def list_service_instance_detail(self) -> Operation:
        """
        bkapi resource list_service_instance_detail
        获取服务实例详细信息
        """
    @property
    def list_service_template(self) -> Operation:
        """
        bkapi resource list_service_template
        服务模板列表查询
        """
    @property
    def list_service_template_difference(self) -> Operation:
        """
        bkapi resource list_service_template_difference
        列出服务模版和服务实例之间的差异
        """
    @property
    def list_set_template(self) -> Operation:
        """
        bkapi resource list_set_template
        查询集群模板
        """
    @property
    def list_set_template_related_service_template(self) -> Operation:
        """
        bkapi resource list_set_template_related_service_template
        获取某集群模版下的服务模版列表
        """
    @property
    def post_auth_skip_url(self) -> Operation:
        """
        bkapi resource post_auth_skip_url
        post_auth_skip_url
        """
    @property
    def post_auth_verify(self) -> Operation:
        """
        bkapi resource post_auth_verify
        post_auth_verify
        """
    @property
    def post_cloud_account_verify(self) -> Operation:
        """
        bkapi resource post_cloud_account_verify
        post_cloud_account_verify
        """
    @property
    def post_count_topoassociationtype(self) -> Operation:
        """
        bkapi resource post_count_topoassociationtype
        post_count_topoassociationtype
        """
    @property
    def post_count_topoinst_host_service_inst_biz_set(self) -> Operation:
        """
        bkapi resource post_count_topoinst_host_service_inst_biz_set
        post_count_topoinst_host_service_inst_biz_set
        """
    @property
    def post_create_associationtype(self) -> Operation:
        """
        bkapi resource post_create_associationtype
        post_create_associationtype
        """
    @property
    def post_create_cloud_account(self) -> Operation:
        """
        bkapi resource post_create_cloud_account
        post_create_cloud_account
        """
    @property
    def post_create_cloud_sync_task(self) -> Operation:
        """
        bkapi resource post_create_cloud_sync_task
        post_create_cloud_sync_task
        """
    @property
    def post_create_field_template(self) -> Operation:
        """
        bkapi resource post_create_field_template
        post_create_field_template
        """
    @property
    def post_create_field_template_clone(self) -> Operation:
        """
        bkapi resource post_create_field_template_clone
        post_create_field_template_clone
        """
    @property
    def post_create_objectassociation(self) -> Operation:
        """
        bkapi resource post_create_objectassociation
        post_create_objectassociation
        """
    @property
    def post_create_objectattgroup(self) -> Operation:
        """
        bkapi resource post_create_objectattgroup
        post_create_objectattgroup
        """
    @property
    def post_create_objectunique_object(self) -> Operation:
        """
        bkapi resource post_create_objectunique_object
        post_create_objectunique_object
        """
    @property
    def post_create_operation_chart(self) -> Operation:
        """
        bkapi resource post_create_operation_chart
        post_create_operation_chart
        """
    @property
    def post_create_proc_service_template_all_info(self) -> Operation:
        """
        bkapi resource post_create_proc_service_template_all_info
        post_create_proc_service_template_all_info
        """
    @property
    def post_create_resource_directory(self) -> Operation:
        """
        bkapi resource post_create_resource_directory
        post_create_resource_directory
        """
    @property
    def post_create_topo_set_template_all_info(self) -> Operation:
        """
        bkapi resource post_create_topo_set_template_all_info
        post_create_topo_set_template_all_info
        """
    @property
    def post_create_topomodelmainline(self) -> Operation:
        """
        bkapi resource post_create_topomodelmainline
        post_create_topomodelmainline
        """
    @property
    def post_createmany_cloudarea(self) -> Operation:
        """
        bkapi resource post_createmany_cloudarea
        post_createmany_cloudarea
        """
    @property
    def post_delete_objectunique_object__unique(self) -> Operation:
        """
        bkapi resource post_delete_objectunique_object__unique
        post_delete_objectunique_object__unique
        """
    @property
    def post_find_associationtype(self) -> Operation:
        """
        bkapi resource post_find_associationtype
        post_find_associationtype
        """
    @property
    def post_find_biz_set_preview(self) -> Operation:
        """
        bkapi resource post_find_biz_set_preview
        post_find_biz_set_preview
        """
    @property
    def post_find_classificationobject(self) -> Operation:
        """
        bkapi resource post_find_classificationobject
        post_find_classificationobject
        """
    @property
    def post_find_field_template_attribute_difference(self) -> Operation:
        """
        bkapi resource post_find_field_template_attribute_difference
        post_find_field_template_attribute_difference
        """
    @property
    def post_find_field_template_model_status(self) -> Operation:
        """
        bkapi resource post_find_field_template_model_status
        post_find_field_template_model_status
        """
    @property
    def post_find_field_template_simplify_by_attr_template_id(self) -> Operation:
        """
        bkapi resource post_find_field_template_simplify_by_attr_template_id
        post_find_field_template_simplify_by_attr_template_id
        """
    @property
    def post_find_field_template_sync_status(self) -> Operation:
        """
        bkapi resource post_find_field_template_sync_status
        post_find_field_template_sync_status
        """
    @property
    def post_find_field_template_tasks_status(self) -> Operation:
        """
        bkapi resource post_find_field_template_tasks_status
        post_find_field_template_tasks_status
        """
    @property
    def post_find_field_template_unique_difference(self) -> Operation:
        """
        bkapi resource post_find_field_template_unique_difference
        post_find_field_template_unique_difference
        """
    @property
    def post_find_full_text(self) -> Operation:
        """
        bkapi resource post_find_full_text
        post_find_full_text
        """
    @property
    def post_find_host_topopath(self) -> Operation:
        """
        bkapi resource post_find_host_topopath
        post_find_host_topopath
        """
    @property
    def post_find_inst_audit(self) -> Operation:
        """
        bkapi resource post_find_inst_audit
        post_find_inst_audit
        """
    @property
    def post_find_instassociation_biz(self) -> Operation:
        """
        bkapi resource post_find_instassociation_biz
        post_find_instassociation_biz
        """
    @property
    def post_find_kube_host_node_path(self) -> Operation:
        """
        bkapi resource post_find_kube_host_node_path
        post_find_kube_host_node_path
        """
    @property
    def post_find_kube_pod_path(self) -> Operation:
        """
        bkapi resource post_find_kube_pod_path
        post_find_kube_pod_path
        """
    @property
    def post_find_kube_topo_node_count(self) -> Operation:
        """
        bkapi resource post_find_kube_topo_node_count
        post_find_kube_topo_node_count
        """
    @property
    def post_find_kube_topo_path(self) -> Operation:
        """
        bkapi resource post_find_kube_topo_path
        post_find_kube_topo_path
        """
    @property
    def post_find_objecttopo_scope_type_global_scope_id_0(self) -> Operation:
        """
        bkapi resource post_find_objecttopo_scope_type_global_scope_id_0
        post_find_objecttopo_scope_type_global_scope_id_0
        """
    @property
    def post_find_operation_chart_data(self) -> Operation:
        """
        bkapi resource post_find_operation_chart_data
        post_find_operation_chart_data
        """
    @property
    def post_find_proc_biz_set__proc_template_id(self) -> Operation:
        """
        bkapi resource post_find_proc_biz_set__proc_template_id
        post_find_proc_biz_set__proc_template_id
        """
    @property
    def post_find_proc_difference_service_instances(self) -> Operation:
        """
        bkapi resource post_find_proc_difference_service_instances
        post_find_proc_difference_service_instances
        """
    @property
    def post_find_proc_service_instance_difference_detail(self) -> Operation:
        """
        bkapi resource post_find_proc_service_instance_difference_detail
        post_find_proc_service_instance_difference_detail
        """
    @property
    def post_find_proc_service_template_all_info(self) -> Operation:
        """
        bkapi resource post_find_proc_service_template_all_info
        post_find_proc_service_template_all_info
        """
    @property
    def post_find_proc_service_template_general_difference(self) -> Operation:
        """
        bkapi resource post_find_proc_service_template_general_difference
        post_find_proc_service_template_general_difference
        """
    @property
    def post_find_proc_service_template_host_apply_rule_related(self) -> Operation:
        """
        bkapi resource post_find_proc_service_template_host_apply_rule_related
        post_find_proc_service_template_host_apply_rule_related
        """
    @property
    def post_find_topo_set_template_all_info(self) -> Operation:
        """
        bkapi resource post_find_topo_set_template_all_info
        post_find_topo_set_template_all_info
        """
    @property
    def post_find_topoinst_bk_biz_id__host_apply_rule_related(self) -> Operation:
        """
        bkapi resource post_find_topoinst_bk_biz_id__host_apply_rule_related
        post_find_topoinst_bk_biz_id__host_apply_rule_related
        """
    @property
    def post_find_topoinst_with_statistics_biz(self) -> Operation:
        """
        bkapi resource post_find_topoinst_with_statistics_biz
        post_find_topoinst_with_statistics_biz
        """
    @property
    def post_find_topoinstnode_host_serviceinst_count(self) -> Operation:
        """
        bkapi resource post_find_topoinstnode_host_serviceinst_count
        post_find_topoinstnode_host_serviceinst_count
        """
    @property
    def post_find_topopath_biz(self) -> Operation:
        """
        bkapi resource post_find_topopath_biz
        post_find_topopath_biz
        """
    @property
    def post_find_topopath_biz_set__biz(self) -> Operation:
        """
        bkapi resource post_find_topopath_biz_set__biz
        post_find_topopath_biz_set__biz
        """
    @property
    def post_findmany_cloud_account(self) -> Operation:
        """
        bkapi resource post_findmany_cloud_account
        post_findmany_cloud_account
        """
    @property
    def post_findmany_cloud_account_validity(self) -> Operation:
        """
        bkapi resource post_findmany_cloud_account_validity
        post_findmany_cloud_account_validity
        """
    @property
    def post_findmany_cloud_account_vpc(self) -> Operation:
        """
        bkapi resource post_findmany_cloud_account_vpc
        post_findmany_cloud_account_vpc
        """
    @property
    def post_findmany_cloud_sync_history(self) -> Operation:
        """
        bkapi resource post_findmany_cloud_sync_history
        post_findmany_cloud_sync_history
        """
    @property
    def post_findmany_cloud_sync_region(self) -> Operation:
        """
        bkapi resource post_findmany_cloud_sync_region
        post_findmany_cloud_sync_region
        """
    @property
    def post_findmany_cloud_sync_task(self) -> Operation:
        """
        bkapi resource post_findmany_cloud_sync_task
        post_findmany_cloud_sync_task
        """
    @property
    def post_findmany_cloudarea_hostcount(self) -> Operation:
        """
        bkapi resource post_findmany_cloudarea_hostcount
        post_findmany_cloudarea_hostcount
        """
    @property
    def post_findmany_field_template_attribute_count(self) -> Operation:
        """
        bkapi resource post_findmany_field_template_attribute_count
        post_findmany_field_template_attribute_count
        """
    @property
    def post_findmany_field_template_by_object(self) -> Operation:
        """
        bkapi resource post_findmany_field_template_by_object
        post_findmany_field_template_by_object
        """
    @property
    def post_findmany_field_template_object_count(self) -> Operation:
        """
        bkapi resource post_findmany_field_template_object_count
        post_findmany_field_template_object_count
        """
    @property
    def post_findmany_field_template_unique(self) -> Operation:
        """
        bkapi resource post_findmany_field_template_unique
        post_findmany_field_template_unique
        """
    @property
    def post_findmany_host_apply_rule_bk_biz_id(self) -> Operation:
        """
        bkapi resource post_findmany_host_apply_rule_bk_biz_id
        post_findmany_host_apply_rule_bk_biz_id
        """
    @property
    def post_findmany_host_apply_rule_bk_biz_id__host_related_rules(self) -> Operation:
        """
        bkapi resource post_findmany_host_apply_rule_bk_biz_id__host_related_rules
        post_findmany_host_apply_rule_bk_biz_id__host_related_rules
        """
    @property
    def post_findmany_hosts_biz_set(self) -> Operation:
        """
        bkapi resource post_findmany_hosts_biz_set
        post_findmany_hosts_biz_set
        """
    @property
    def post_findmany_hosts_search_noauth(self) -> Operation:
        """
        bkapi resource post_findmany_hosts_search_noauth
        post_findmany_hosts_search_noauth
        """
    @property
    def post_findmany_hosts_search_resource(self) -> Operation:
        """
        bkapi resource post_findmany_hosts_search_resource
        post_findmany_hosts_search_resource
        """
    @property
    def post_findmany_hosts_search_with_biz(self) -> Operation:
        """
        bkapi resource post_findmany_hosts_search_with_biz
        post_findmany_hosts_search_with_biz
        """
    @property
    def post_findmany_inst_association_object__inst_id__offset__limit__web(self) -> Operation:
        """
        bkapi resource post_findmany_inst_association_object__inst_id__offset__limit__web
        post_findmany_inst_association_object__inst_id__offset__limit__web
        """
    @property
    def post_findmany_module_biz_set__biz__set(self) -> Operation:
        """
        bkapi resource post_findmany_module_biz_set__biz__set
        post_findmany_module_biz_set__biz__set
        """
    @property
    def post_findmany_object_by_field_template(self) -> Operation:
        """
        bkapi resource post_findmany_object_by_field_template
        post_findmany_object_by_field_template
        """
    @property
    def post_findmany_object_instances_names(self) -> Operation:
        """
        bkapi resource post_findmany_object_instances_names
        post_findmany_object_instances_names
        """
    @property
    def post_findmany_proc_biz_set__proc_template(self) -> Operation:
        """
        bkapi resource post_findmany_proc_biz_set__proc_template
        post_findmany_proc_biz_set__proc_template
        """
    @property
    def post_findmany_proc_biz_set__process_instance(self) -> Operation:
        """
        bkapi resource post_findmany_proc_biz_set__process_instance
        post_findmany_proc_biz_set__process_instance
        """
    @property
    def post_findmany_proc_biz_set__process_instance_detail_by_ids(self) -> Operation:
        """
        bkapi resource post_findmany_proc_biz_set__process_instance_detail_by_ids
        post_findmany_proc_biz_set__process_instance_detail_by_ids
        """
    @property
    def post_findmany_proc_biz_set__process_instance_name_ids(self) -> Operation:
        """
        bkapi resource post_findmany_proc_biz_set__process_instance_name_ids
        post_findmany_proc_biz_set__process_instance_name_ids
        """
    @property
    def post_findmany_proc_biz_set__service_instance_labels_aggregation(self) -> Operation:
        """
        bkapi resource post_findmany_proc_biz_set__service_instance_labels_aggregation
        post_findmany_proc_biz_set__service_instance_labels_aggregation
        """
    @property
    def post_findmany_proc_biz_set_service_instance(self) -> Operation:
        """
        bkapi resource post_findmany_proc_biz_set_service_instance
        post_findmany_proc_biz_set_service_instance
        """
    @property
    def post_findmany_proc_biz_set_service_instance_with_host(self) -> Operation:
        """
        bkapi resource post_findmany_proc_biz_set_service_instance_with_host
        post_findmany_proc_biz_set_service_instance_with_host
        """
    @property
    def post_findmany_proc_host_with_no_service_instance(self) -> Operation:
        """
        bkapi resource post_findmany_proc_host_with_no_service_instance
        post_findmany_proc_host_with_no_service_instance
        """
    @property
    def post_findmany_proc_process_instance_detail_by_ids(self) -> Operation:
        """
        bkapi resource post_findmany_proc_process_instance_detail_by_ids
        post_findmany_proc_process_instance_detail_by_ids
        """
    @property
    def post_findmany_proc_process_instance_name_ids(self) -> Operation:
        """
        bkapi resource post_findmany_proc_process_instance_name_ids
        post_findmany_proc_process_instance_name_ids
        """
    @property
    def post_findmany_proc_service_category_with_statistics(self) -> Operation:
        """
        bkapi resource post_findmany_proc_service_category_with_statistics
        post_findmany_proc_service_category_with_statistics
        """
    @property
    def post_findmany_proc_service_instance_labels_aggregation(self) -> Operation:
        """
        bkapi resource post_findmany_proc_service_instance_labels_aggregation
        post_findmany_proc_service_instance_labels_aggregation
        """
    @property
    def post_findmany_proc_service_template_attribute(self) -> Operation:
        """
        bkapi resource post_findmany_proc_service_template_attribute
        post_findmany_proc_service_template_attribute
        """
    @property
    def post_findmany_proc_service_template_count_info_biz(self) -> Operation:
        """
        bkapi resource post_findmany_proc_service_template_count_info_biz
        post_findmany_proc_service_template_count_info_biz
        """
    @property
    def post_findmany_proc_service_template_host_apply_plan_status(self) -> Operation:
        """
        bkapi resource post_findmany_proc_service_template_host_apply_plan_status
        post_findmany_proc_service_template_host_apply_plan_status
        """
    @property
    def post_findmany_proc_service_template_sync_status_bk_biz_id(self) -> Operation:
        """
        bkapi resource post_findmany_proc_service_template_sync_status_bk_biz_id
        post_findmany_proc_service_template_sync_status_bk_biz_id
        """
    @property
    def post_findmany_resource_directory(self) -> Operation:
        """
        bkapi resource post_findmany_resource_directory
        post_findmany_resource_directory
        """
    @property
    def post_findmany_set_biz_set__biz(self) -> Operation:
        """
        bkapi resource post_findmany_set_biz_set__biz
        post_findmany_set_biz_set__biz
        """
    @property
    def post_findmany_topo_set_template__bk_biz_id__diff_with_instances(self) -> Operation:
        """
        bkapi resource post_findmany_topo_set_template__bk_biz_id__diff_with_instances
        post_findmany_topo_set_template__bk_biz_id__diff_with_instances
        """
    @property
    def post_findmany_topo_set_template__bk_biz_id__host_with_instances(self) -> Operation:
        """
        bkapi resource post_findmany_topo_set_template__bk_biz_id__host_with_instances
        post_findmany_topo_set_template__bk_biz_id__host_with_instances
        """
    @property
    def post_findmany_topo_set_template__bk_biz_id__instances_sync_status(self) -> Operation:
        """
        bkapi resource post_findmany_topo_set_template__bk_biz_id__instances_sync_status
        post_findmany_topo_set_template__bk_biz_id__instances_sync_status
        """
    @property
    def post_findmany_topo_set_template__bk_biz_id__sets_web(self) -> Operation:
        """
        bkapi resource post_findmany_topo_set_template__bk_biz_id__sets_web
        post_findmany_topo_set_template__bk_biz_id__sets_web
        """
    @property
    def post_findmany_topo_set_template_attribute(self) -> Operation:
        """
        bkapi resource post_findmany_topo_set_template_attribute
        post_findmany_topo_set_template_attribute
        """
    @property
    def post_findmany_topo_set_template_bk_biz_id__set_template_status(self) -> Operation:
        """
        bkapi resource post_findmany_topo_set_template_bk_biz_id__set_template_status
        post_findmany_topo_set_template_bk_biz_id__set_template_status
        """
    @property
    def post_findmany_topo_set_template_bk_biz_id__web(self) -> Operation:
        """
        bkapi resource post_findmany_topo_set_template_bk_biz_id__web
        post_findmany_topo_set_template_bk_biz_id__web
        """
    @property
    def post_findmany_topo_set_template_sync_history_bk_biz_id(self) -> Operation:
        """
        bkapi resource post_findmany_topo_set_template_sync_history_bk_biz_id
        post_findmany_topo_set_template_sync_history_bk_biz_id
        """
    @property
    def post_findmany_topo_set_template_sync_status_bk_biz_id(self) -> Operation:
        """
        bkapi resource post_findmany_topo_set_template_sync_status_bk_biz_id
        post_findmany_topo_set_template_sync_status_bk_biz_id
        """
    @property
    def post_host_createmany_module_host_apply_plan_preview(self) -> Operation:
        """
        bkapi resource post_host_createmany_module_host_apply_plan_preview
        post_host_createmany_module_host_apply_plan_preview
        """
    @property
    def post_host_createmany_service_template_host_apply_plan_preview(self) -> Operation:
        """
        bkapi resource post_host_createmany_service_template_host_apply_plan_preview
        post_host_createmany_service_template_host_apply_plan_preview
        """
    @property
    def post_host_find_service_template_host_apply_status(self) -> Operation:
        """
        bkapi resource post_host_find_service_template_host_apply_status
        post_host_find_service_template_host_apply_status
        """
    @property
    def post_host_findmany_module_get_module_final_rules(self) -> Operation:
        """
        bkapi resource post_host_findmany_module_get_module_final_rules
        post_host_findmany_module_get_module_final_rules
        """
    @property
    def post_host_findmany_module_host_apply_plan_invalid_host_count(self) -> Operation:
        """
        bkapi resource post_host_findmany_module_host_apply_plan_invalid_host_count
        post_host_findmany_module_host_apply_plan_invalid_host_count
        """
    @property
    def post_host_findmany_module_host_apply_plan_status(self) -> Operation:
        """
        bkapi resource post_host_findmany_module_host_apply_plan_status
        post_host_findmany_module_host_apply_plan_status
        """
    @property
    def post_host_findmany_service_template_host_apply_plan_invalid_host_count(self) -> Operation:
        """
        bkapi resource post_host_findmany_service_template_host_apply_plan_invalid_host_count
        post_host_findmany_service_template_host_apply_plan_invalid_host_count
        """
    @property
    def post_host_findmany_service_template_host_apply_rule(self) -> Operation:
        """
        bkapi resource post_host_findmany_service_template_host_apply_rule
        post_host_findmany_service_template_host_apply_rule
        """
    @property
    def post_host_findmany_service_template_host_apply_rule_count(self) -> Operation:
        """
        bkapi resource post_host_findmany_service_template_host_apply_rule_count
        post_host_findmany_service_template_host_apply_rule_count
        """
    @property
    def post_host_transfer_resource_directory(self) -> Operation:
        """
        bkapi resource post_host_transfer_resource_directory
        post_host_transfer_resource_directory
        """
    @property
    def post_host_transfer_with_auto_clear_service_instance_bk_biz_id(self) -> Operation:
        """
        bkapi resource post_host_transfer_with_auto_clear_service_instance_bk_biz_id
        post_host_transfer_with_auto_clear_service_instance_bk_biz_id
        """
    @property
    def post_host_transfer_with_auto_clear_service_instance_bk_biz_id__preview(self) -> Operation:
        """
        bkapi resource post_host_transfer_with_auto_clear_service_instance_bk_biz_id__preview
        post_host_transfer_with_auto_clear_service_instance_bk_biz_id__preview
        """
    @property
    def post_host_updatemany_module_host_apply_plan_run(self) -> Operation:
        """
        bkapi resource post_host_updatemany_module_host_apply_plan_run
        post_host_updatemany_module_host_apply_plan_run
        """
    @property
    def post_hosts_favorites(self) -> Operation:
        """
        bkapi resource post_hosts_favorites
        post_hosts_favorites
        """
    @property
    def post_hosts_favorites_search(self) -> Operation:
        """
        bkapi resource post_hosts_favorites_search
        post_hosts_favorites_search
        """
    @property
    def post_hosts_import(self) -> Operation:
        """
        bkapi resource post_hosts_import
        post_hosts_import
        """
    @property
    def post_hosts_kube_search(self) -> Operation:
        """
        bkapi resource post_hosts_kube_search
        post_hosts_kube_search
        """
    @property
    def post_hosts_modules_biz_mutilple(self) -> Operation:
        """
        bkapi resource post_hosts_modules_biz_mutilple
        post_hosts_modules_biz_mutilple
        """
    @property
    def post_hosts_resource_cross_biz(self) -> Operation:
        """
        bkapi resource post_hosts_resource_cross_biz
        post_hosts_resource_cross_biz
        """
    @property
    def post_hosts_search(self) -> Operation:
        """
        bkapi resource post_hosts_search
        post_hosts_search
        """
    @property
    def post_module_bk_biz_id__service_template_id(self) -> Operation:
        """
        bkapi resource post_module_bk_biz_id__service_template_id
        post_module_bk_biz_id__service_template_id
        """
    @property
    def post_set__batch(self) -> Operation:
        """
        bkapi resource post_set__batch
        post_set__batch
        """
    @property
    def post_shipper_find_srv_status_scene_type(self) -> Operation:
        """
        bkapi resource post_shipper_find_srv_status_scene_type
        post_shipper_find_srv_status_scene_type
        """
    @property
    def post_shipper_findmany_special_biz(self) -> Operation:
        """
        bkapi resource post_shipper_findmany_special_biz
        post_shipper_findmany_special_biz
        """
    @property
    def post_shipper_sync_nieg_host(self) -> Operation:
        """
        bkapi resource post_shipper_sync_nieg_host
        post_shipper_sync_nieg_host
        """
    @property
    def post_sidecar_delete_nieg_host(self) -> Operation:
        """
        bkapi resource post_sidecar_delete_nieg_host
        post_sidecar_delete_nieg_host
        """
    @property
    def post_sidecar_findmany_company_host(self) -> Operation:
        """
        bkapi resource post_sidecar_findmany_company_host
        post_sidecar_findmany_company_host
        """
    @property
    def post_sidecar_import_nieg_host(self) -> Operation:
        """
        bkapi resource post_sidecar_import_nieg_host
        post_sidecar_import_nieg_host
        """
    @property
    def post_sidecar_itsm_create_ticket(self) -> Operation:
        """
        bkapi resource post_sidecar_itsm_create_ticket
        post_sidecar_itsm_create_ticket
        """
    @property
    def post_system_config_user_config_blueking_modify(self) -> Operation:
        """
        bkapi resource post_system_config_user_config_blueking_modify
        post_system_config_user_config_blueking_modify
        """
    @property
    def post_topo_delete_biz_extra_moudle(self) -> Operation:
        """
        bkapi resource post_topo_delete_biz_extra_moudle
        post_topo_delete_biz_extra_moudle
        """
    @property
    def post_topo_update_biz_idle_set(self) -> Operation:
        """
        bkapi resource post_topo_update_biz_idle_set
        post_topo_update_biz_idle_set
        """
    @property
    def post_update_field_template_bind_object(self) -> Operation:
        """
        bkapi resource post_update_field_template_bind_object
        post_update_field_template_bind_object
        """
    @property
    def post_update_field_template_unbind_object(self) -> Operation:
        """
        bkapi resource post_update_field_template_unbind_object
        post_update_field_template_unbind_object
        """
    @property
    def post_update_objectattr_index(self) -> Operation:
        """
        bkapi resource post_update_objectattr_index
        post_update_objectattr_index
        """
    @property
    def post_update_objecttopo_scope_type_global_scope_id_0(self) -> Operation:
        """
        bkapi resource post_update_objecttopo_scope_type_global_scope_id_0
        post_update_objecttopo_scope_type_global_scope_id_0
        """
    @property
    def post_update_operation_chart(self) -> Operation:
        """
        bkapi resource post_update_operation_chart
        post_update_operation_chart
        """
    @property
    def post_update_operation_chart_position(self) -> Operation:
        """
        bkapi resource post_update_operation_chart_position
        post_update_operation_chart_position
        """
    @property
    def post_update_topo_field_template_sync(self) -> Operation:
        """
        bkapi resource post_update_topo_field_template_sync
        post_update_topo_field_template_sync
        """
    @property
    def post_updatemany_proc_service_instance_labels(self) -> Operation:
        """
        bkapi resource post_updatemany_proc_service_instance_labels
        post_updatemany_proc_service_instance_labels
        """
    @property
    def post_updatemany_proc_service_template_host_apply_plan_run(self) -> Operation:
        """
        bkapi resource post_updatemany_proc_service_template_host_apply_plan_run
        post_updatemany_proc_service_template_host_apply_plan_run
        """
    @property
    def post_usercustom(self) -> Operation:
        """
        bkapi resource post_usercustom
        post_usercustom
        """
    @property
    def post_usercustom_default_model(self) -> Operation:
        """
        bkapi resource post_usercustom_default_model
        post_usercustom_default_model
        """
    @property
    def post_usercustom_default_model_sub(self) -> Operation:
        """
        bkapi resource post_usercustom_default_model_sub
        post_usercustom_default_model_sub
        """
    @property
    def post_usercustom_default_search(self) -> Operation:
        """
        bkapi resource post_usercustom_default_search
        post_usercustom_default_search
        """
    @property
    def post_usercustom_user_search(self) -> Operation:
        """
        bkapi resource post_usercustom_user_search
        post_usercustom_user_search
        """
    @property
    def push_host_identifier(self) -> Operation:
        """
        bkapi resource push_host_identifier
        推送主机身份
        """
    @property
    def put_biz_status_disabled(self) -> Operation:
        """
        bkapi resource put_biz_status_disabled
        put_biz_status_disabled
        """
    @property
    def put_biz_status_enable(self) -> Operation:
        """
        bkapi resource put_biz_status_enable
        put_biz_status_enable
        """
    @property
    def put_hosts_favorites(self) -> Operation:
        """
        bkapi resource put_hosts_favorites
        put_hosts_favorites
        """
    @property
    def put_hosts_favorites__incr(self) -> Operation:
        """
        bkapi resource put_hosts_favorites__incr
        put_hosts_favorites__incr
        """
    @property
    def put_module_host_apply_enable_status_bk_biz_id(self) -> Operation:
        """
        bkapi resource put_module_host_apply_enable_status_bk_biz_id
        put_module_host_apply_enable_status_bk_biz_id
        """
    @property
    def put_update_associationtype(self) -> Operation:
        """
        bkapi resource put_update_associationtype
        put_update_associationtype
        """
    @property
    def put_update_cloud_account(self) -> Operation:
        """
        bkapi resource put_update_cloud_account
        put_update_cloud_account
        """
    @property
    def put_update_cloud_sync_task(self) -> Operation:
        """
        bkapi resource put_update_cloud_sync_task
        put_update_cloud_sync_task
        """
    @property
    def put_update_field_template(self) -> Operation:
        """
        bkapi resource put_update_field_template
        put_update_field_template
        """
    @property
    def put_update_field_template_info(self) -> Operation:
        """
        bkapi resource put_update_field_template_info
        put_update_field_template_info
        """
    @property
    def put_update_objectassociation(self) -> Operation:
        """
        bkapi resource put_update_objectassociation
        put_update_objectassociation
        """
    @property
    def put_update_objectattgroup(self) -> Operation:
        """
        bkapi resource put_update_objectattgroup
        put_update_objectattgroup
        """
    @property
    def put_update_objectattgroup_groupindex(self) -> Operation:
        """
        bkapi resource put_update_objectattgroup_groupindex
        put_update_objectattgroup_groupindex
        """
    @property
    def put_update_objectunique_object__unique(self) -> Operation:
        """
        bkapi resource put_update_objectunique_object__unique
        put_update_objectunique_object__unique
        """
    @property
    def put_update_proc_process_instance_by_ids(self) -> Operation:
        """
        bkapi resource put_update_proc_process_instance_by_ids
        put_update_proc_process_instance_by_ids
        """
    @property
    def put_update_proc_service_instance_sync(self) -> Operation:
        """
        bkapi resource put_update_proc_service_instance_sync
        put_update_proc_service_instance_sync
        """
    @property
    def put_update_proc_service_template_all_info(self) -> Operation:
        """
        bkapi resource put_update_proc_service_template_all_info
        put_update_proc_service_template_all_info
        """
    @property
    def put_update_proc_service_template_attribute(self) -> Operation:
        """
        bkapi resource put_update_proc_service_template_attribute
        put_update_proc_service_template_attribute
        """
    @property
    def put_update_resource_directory(self) -> Operation:
        """
        bkapi resource put_update_resource_directory
        put_update_resource_directory
        """
    @property
    def put_update_topo_set_template_all_info(self) -> Operation:
        """
        bkapi resource put_update_topo_set_template_all_info
        put_update_topo_set_template_all_info
        """
    @property
    def put_update_topo_set_template_attribute(self) -> Operation:
        """
        bkapi resource put_update_topo_set_template_attribute
        put_update_topo_set_template_attribute
        """
    @property
    def put_updatemany_proc_service_instance_biz(self) -> Operation:
        """
        bkapi resource put_updatemany_proc_service_instance_biz
        put_updatemany_proc_service_instance_biz
        """
    @property
    def put_updatemany_proc_service_template_host_apply_enable_status_biz(self) -> Operation:
        """
        bkapi resource put_updatemany_proc_service_template_host_apply_enable_status_biz
        put_updatemany_proc_service_template_host_apply_enable_status_biz
        """
    @property
    def read_instance(self) -> Operation:
        """
        bkapi resource read_instance
        ReadInstance
        """
    @property
    def read_model(self) -> Operation:
        """
        bkapi resource read_model
        ReadModel
        """
    @property
    def read_model_for_ui(self) -> Operation:
        """
        bkapi resource read_model_for_ui
        ReadModelForUI
        """
    @property
    def read_module_association(self) -> Operation:
        """
        bkapi resource read_module_association
        ReadModuleAssociation
        """
    @property
    def remove_label_from_service_instance(self) -> Operation:
        """
        bkapi resource remove_label_from_service_instance
        从服务实例移除标签
        """
    @property
    def resource_watch(self) -> Operation:
        """
        bkapi resource resource_watch
        监听资源变化事件
        """
    @property
    def search_biz_inst_topo(self) -> Operation:
        """
        bkapi resource search_biz_inst_topo
        查询业务实例拓扑
        """
    @property
    def search_business(self) -> Operation:
        """
        bkapi resource search_business
        查询业务
        """
    @property
    def search_classifications(self) -> Operation:
        """
        bkapi resource search_classifications
        查询模型分类
        """
    @property
    def search_cloud_area(self) -> Operation:
        """
        bkapi resource search_cloud_area
        查询管控区域
        """
    @property
    def search_cmpy_business1(self) -> Operation:
        """
        bkapi resource search_cmpy_business1
        查询公司cmdb的一级业务
        """
    @property
    def search_cmpy_business2(self) -> Operation:
        """
        bkapi resource search_cmpy_business2
        查询公司cmdb的二级业务
        """
    @property
    def search_cmpy_business3(self) -> Operation:
        """
        bkapi resource search_cmpy_business3
        查询公司cmdb的三级业务
        """
    @property
    def search_cmpy_businessdept(self) -> Operation:
        """
        bkapi resource search_cmpy_businessdept
        查询公司cmdb的部门
        """
    @property
    def search_cost_info_relation(self) -> Operation:
        """
        bkapi resource search_cost_info_relation
        查询业务、obs产品和规划产品三者之间的关系
        """
    @property
    def search_default_app(self) -> Operation:
        """
        bkapi resource search_default_app
        SearchDefaultApp
        """
    @property
    def search_dynamic_group(self) -> Operation:
        """
        bkapi resource search_dynamic_group
        搜索动态分组
        """
    @property
    def search_host_lock(self) -> Operation:
        """
        bkapi resource search_host_lock
        查询主机锁
        """
    @property
    def search_hostidentifier(self) -> Operation:
        """
        bkapi resource search_hostidentifier
        根据条件查询主机身份
        """
    @property
    def search_inst(self) -> Operation:
        """
        bkapi resource search_inst
        根据关联关系实例查询模型实例
        """
    @property
    def search_inst_association_topo(self) -> Operation:
        """
        bkapi resource search_inst_association_topo
        查询实例关联拓扑
        """
    @property
    def search_inst_asst_object_inst_base_info(self) -> Operation:
        """
        bkapi resource search_inst_asst_object_inst_base_info
        查询实例关联模型实例基本信息
        """
    @property
    def search_inst_by_object(self) -> Operation:
        """
        bkapi resource search_inst_by_object
        查询实例详情
        """
    @property
    def search_instance_associations(self) -> Operation:
        """
        bkapi resource search_instance_associations
        查询模型实例关系
        """
    @property
    def search_module(self) -> Operation:
        """
        bkapi resource search_module
        查询模块
        """
    @property
    def search_net_collect_device(self) -> Operation:
        """
        bkapi resource search_net_collect_device
        SearchNetCollectDevice
        """
    @property
    def search_net_collect_device_batch(self) -> Operation:
        """
        bkapi resource search_net_collect_device_batch
        SearchNetCollectDeviceBatch
        """
    @property
    def search_net_device_property(self) -> Operation:
        """
        bkapi resource search_net_device_property
        SearchNetDeviceProperty
        """
    @property
    def search_net_device_property_batch(self) -> Operation:
        """
        bkapi resource search_net_device_property_batch
        SearchNetDevicePropertyBatch
        """
    @property
    def search_object_attribute(self) -> Operation:
        """
        bkapi resource search_object_attribute
        查询对象模型属性
        """
    @property
    def search_object_instances(self) -> Operation:
        """
        bkapi resource search_object_instances
        查询模型实例
        """
    @property
    def search_object_topo(self) -> Operation:
        """
        bkapi resource search_object_topo
        查询普通模型拓扑
        """
    @property
    def search_object_unique(self) -> Operation:
        """
        bkapi resource search_object_unique
        SearchObjectUnique
        """
    @property
    def search_object_with_total_info(self) -> Operation:
        """
        bkapi resource search_object_with_total_info
        SearchObjectWithTotalInfo
        """
    @property
    def search_objects(self) -> Operation:
        """
        bkapi resource search_objects
        查询模型
        """
    @property
    def search_platform_setting(self) -> Operation:
        """
        bkapi resource search_platform_setting
        SearchPlatformSetting
        """
    @property
    def search_process_instances(self) -> Operation:
        """
        bkapi resource search_process_instances
        根据条件查询业务下的进程实例详情
        """
    @property
    def search_related_inst_asso(self) -> Operation:
        """
        bkapi resource search_related_inst_asso
        查询某实例所有的关联关系（包含其作为关联关系原模型和关联关系目标模型的情况）
        """
    @property
    def search_set(self) -> Operation:
        """
        bkapi resource search_set
        查询集群
        """
    @property
    def sync_host_info_from_cmpy(self) -> Operation:
        """
        bkapi resource sync_host_info_from_cmpy
        同步公司cmdb主机详情信息到cc3.0
        """
    @property
    def sync_host_vip_info(self) -> Operation:
        """
        bkapi resource sync_host_vip_info
        从tgw同步主机对应的vip、vport等信息
        """
    @property
    def sync_inst_id_rule(self) -> Operation:
        """
        bkapi resource sync_inst_id_rule
        同步刷新id规则字段值到该字段为空的模型实例
        """
    @property
    def sync_set_template_to_set(self) -> Operation:
        """
        bkapi resource sync_set_template_to_set
        集群模板同步
        """
    @property
    def transfer_host_across_biz(self) -> Operation:
        """
        bkapi resource transfer_host_across_biz
        跨业务转移主机
        """
    @property
    def transfer_host_module(self) -> Operation:
        """
        bkapi resource transfer_host_module
        业务内主机转移模块
        """
    @property
    def transfer_host_to_another_biz(self) -> Operation:
        """
        bkapi resource transfer_host_to_another_biz
        主机交付与转移接口，该接口仅用于跨业务转移主机，不能进行同业务内主机转移。
        """
    @property
    def transfer_host_to_faultmodule(self) -> Operation:
        """
        bkapi resource transfer_host_to_faultmodule
        上交主机到业务的故障机模块
        """
    @property
    def transfer_host_to_idlemodule(self) -> Operation:
        """
        bkapi resource transfer_host_to_idlemodule
        上交主机到业务的空闲机模块
        """
    @property
    def transfer_host_to_recyclemodule(self) -> Operation:
        """
        bkapi resource transfer_host_to_recyclemodule
        上交主机到业务的待回收模块
        """
    @property
    def transfer_host_to_resourcemodule(self) -> Operation:
        """
        bkapi resource transfer_host_to_resourcemodule
        上交主机至资源池
        """
    @property
    def transfer_resourcehost_to_idlemodule(self) -> Operation:
        """
        bkapi resource transfer_resourcehost_to_idlemodule
        资源池主机分配至业务的空闲机模块
        """
    @property
    def transfer_sethost_to_idle_module(self) -> Operation:
        """
        bkapi resource transfer_sethost_to_idle_module
        清空业务下集群/模块中主机
        """
    @property
    def unbind_host_agent(self) -> Operation:
        """
        bkapi resource unbind_host_agent
        将agent和主机解绑
        """
    @property
    def update_biz_custom_field(self) -> Operation:
        """
        bkapi resource update_biz_custom_field
        更新业务自定义模型属性
        """
    @property
    def update_biz_property_batch(self) -> Operation:
        """
        bkapi resource update_biz_property_batch
        UpdateBizPropertyBatch
        """
    @property
    def update_biz_sensitive(self) -> Operation:
        """
        bkapi resource update_biz_sensitive
        更新业务敏感信息
        """
    @property
    def update_business(self) -> Operation:
        """
        bkapi resource update_business
        修改业务
        """
    @property
    def update_business_enable_status(self) -> Operation:
        """
        bkapi resource update_business_enable_status
        修改业务启用状态
        """
    @property
    def update_classification(self) -> Operation:
        """
        bkapi resource update_classification
        更新模型分类
        """
    @property
    def update_cloud_area(self) -> Operation:
        """
        bkapi resource update_cloud_area
        更新管控区域
        """
    @property
    def update_dynamic_group(self) -> Operation:
        """
        bkapi resource update_dynamic_group
        更新动态分组
        """
    @property
    def update_full_sync_cond_for_cache(self) -> Operation:
        """
        bkapi resource update_full_sync_cond_for_cache
        更新全量同步缓存条件信息
        """
    @property
    def update_host(self) -> Operation:
        """
        bkapi resource update_host
        更新主机属性
        """
    @property
    def update_host_cloud_area_field(self) -> Operation:
        """
        bkapi resource update_host_cloud_area_field
        更新主机的管控区域字段
        """
    @property
    def update_id_rule_incr_id(self) -> Operation:
        """
        bkapi resource update_id_rule_incr_id
        更新id规则自增id
        """
    @property
    def update_import_host(self) -> Operation:
        """
        bkapi resource update_import_host
        UpdateHost
        """
    @property
    def update_inst(self) -> Operation:
        """
        bkapi resource update_inst
        更新对象实例
        """
    @property
    def update_kube_cluster_type(self) -> Operation:
        """
        bkapi resource update_kube_cluster_type
        更新容器集群类型
        """
    @property
    def update_module(self) -> Operation:
        """
        bkapi resource update_module
        更新模块
        """
    @property
    def update_object(self) -> Operation:
        """
        bkapi resource update_object
        更新定义
        """
    @property
    def update_object_attribute(self) -> Operation:
        """
        bkapi resource update_object_attribute
        更新对象模型属性
        """
    @property
    def update_object_topo_graphics(self) -> Operation:
        """
        bkapi resource update_object_topo_graphics
        更新拓扑图
        """
    @property
    def update_platform_setting(self) -> Operation:
        """
        bkapi resource update_platform_setting
        UpdatePlatformSetting
        """
    @property
    def update_proc_template(self) -> Operation:
        """
        bkapi resource update_proc_template
        更新进程模板
        """
    @property
    def update_process_instance(self) -> Operation:
        """
        bkapi resource update_process_instance
        更新进程实例
        """
    @property
    def update_project_id(self) -> Operation:
        """
        bkapi resource update_project_id
        更新项目id
        """
    @property
    def update_reinstall_cmdb_cvm(self) -> Operation:
        """
        bkapi resource update_reinstall_cmdb_cvm
        更新公司cmdb中的cvm信息（hcm主机重装专用）
        """
    @property
    def update_service_category(self) -> Operation:
        """
        bkapi resource update_service_category
        更新服务分类
        """
    @property
    def update_service_template(self) -> Operation:
        """
        bkapi resource update_service_template
        更新服务模板
        """
    @property
    def update_set(self) -> Operation:
        """
        bkapi resource update_set
        更新集群
        """
    @property
    def update_set_template(self) -> Operation:
        """
        bkapi resource update_set_template
        编辑集群模板
        """
    @property
    def update_special_biz_host(self) -> Operation:
        """
        bkapi resource update_special_biz_host
        更新特殊业务的主机信息，同步到公司cmdb
        """

class Client(APIGatewayClient):
    """Bkapi bk_cmdb client"""

    @property
    def api(self) -> OperationGroup:
        """api resources"""

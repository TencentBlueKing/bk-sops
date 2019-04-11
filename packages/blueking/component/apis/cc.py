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

from ..base import ComponentAPI


class CollectionsCC(object):
    """Collections of CC APIS"""

    def __init__(self, client):
        self.client = client

        self.add_host_to_resource = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/add_host_to_resource/',
            description=u'新增主机到资源池'
        )
        self.batch_delete_inst = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/batch_delete_inst/',
            description=u'批量删除实例'
        )
        self.batch_delete_set = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/batch_delete_set/',
            description=u'批量删除集群'
        )
        self.batch_update_inst = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/batch_update_inst/',
            description=u'批量更新对象实例'
        )
        self.bind_role_privilege = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/bind_role_privilege/',
            description=u'绑定角色权限'
        )
        self.create_business = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/create_business/',
            description=u'新建业务'
        )
        self.create_classification = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/create_classification/',
            description=u'添加模型分类'
        )
        self.create_custom_query = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/create_custom_query/',
            description=u'添加自定义API'
        )
        self.create_inst = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/create_inst/',
            description=u'创建实例'
        )
        self.create_module = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/create_module/',
            description=u'创建模块'
        )
        self.create_object = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/create_object/',
            description=u'创建模型'
        )
        self.create_object_attribute = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/create_object_attribute/',
            description=u'创建模型属性'
        )
        self.create_set = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/create_set/',
            description=u'创建集群'
        )
        self.create_user_group = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/create_user_group/',
            description=u'新建用户分组'
        )
        self.delete_business = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/delete_business/',
            description=u'删除业务'
        )
        self.delete_classification = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/delete_classification/',
            description=u'删除模型分类'
        )
        self.delete_custom_query = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/delete_custom_query/',
            description=u'删除自定义API'
        )
        self.delete_host = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/delete_host/',
            description=u'删除主机'
        )
        self.delete_inst = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/delete_inst/',
            description=u'删除实例'
        )
        self.delete_module = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/delete_module/',
            description=u'删除模块'
        )
        self.delete_object = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/delete_object/',
            description=u'删除模型'
        )
        self.delete_object_attribute = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/delete_object_attribute/',
            description=u'删除对象模型属性'
        )
        self.delete_set = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/delete_set/',
            description=u'删除集群'
        )
        self.delete_user_group = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/delete_user_group/',
            description=u'删除用户分组'
        )
        self.get_custom_query_data = ComponentAPI(
            client=self.client, method='GET',
            path='/api/c/compapi{bk_api_ver}/cc/get_custom_query_data/',
            description=u'根据自定义api获取数据'
        )
        self.get_custom_query_detail = ComponentAPI(
            client=self.client, method='GET',
            path='/api/c/compapi{bk_api_ver}/cc/get_custom_query_detail/',
            description=u'获取自定义API详情'
        )
        self.get_host_base_info = ComponentAPI(
            client=self.client, method='GET',
            path='/api/c/compapi{bk_api_ver}/cc/get_host_base_info/',
            description=u'获取主机详情'
        )
        self.get_role_privilege = ComponentAPI(
            client=self.client, method='GET',
            path='/api/c/compapi{bk_api_ver}/cc/get_role_privilege/',
            description=u'获取角色绑定权限'
        )
        self.get_user_privilege = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/get_user_privilege/',
            description=u'查询用户权限'
        )
        self.search_biz_inst_topo = ComponentAPI(
            client=self.client, method='GET',
            path='/api/c/compapi{bk_api_ver}/cc/search_biz_inst_topo/',
            description=u'查询业务实例拓扑'
        )
        self.search_business = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/search_business/',
            description=u'查询业务'
        )
        self.search_classifications = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/search_classifications/',
            description=u'查询模型分类'
        )
        self.search_custom_query = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/search_custom_query/',
            description=u'查询自定义API'
        )
        self.search_group_privilege = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/search_group_privilege/',
            description=u'查询分组权限'
        )
        self.search_host = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/search_host/',
            description=u'根据条件查询主机'
        )
        self.search_inst = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/search_inst/',
            description=u'查询实例'
        )
        self.search_inst_association_topo = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/search_inst_association_topo/',
            description=u'查询实例关联拓扑'
        )
        self.search_inst_by_object = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/search_inst_by_object/',
            description=u'查询实例详情'
        )
        self.search_module = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/search_module/',
            description=u'查询模块'
        )
        self.search_object_attribute = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/search_object_attribute/',
            description=u'查询对象模型属性'
        )
        self.search_object_topo = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/search_object_topo/',
            description=u'查询普通模型拓扑'
        )
        self.search_object_topo_graphics = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/search_object_topo_graphics/',
            description=u'查询拓扑图'
        )
        self.search_objects = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/search_objects/',
            description=u'查询模型'
        )
        self.search_set = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/search_set/',
            description=u'查询集群'
        )
        self.search_subscription = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/search_subscription/',
            description=u'查询订阅'
        )
        self.search_user_group = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/search_user_group/',
            description=u'查询用户分组'
        )
        self.subscribe_event = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/subscribe_event/',
            description=u'订阅事件'
        )
        self.testing_connection = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/testing_connection/',
            description=u'测试推送（只测试连通性）'
        )
        self.transfer_host_module = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/transfer_host_module/',
            description=u'业务内主机转移模块'
        )
        self.transfer_host_to_faultmodule = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/transfer_host_to_faultmodule/',
            description=u'上交主机到业务的故障机模块'
        )
        self.transfer_host_to_idlemodule = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/transfer_host_to_idlemodule/',
            description=u'上交主机到业务的空闲机模块'
        )
        self.transfer_host_to_resourcemodule = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/transfer_host_to_resourcemodule/',
            description=u'上交主机至资源池'
        )
        self.transfer_resourcehost_to_idlemodule = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/transfer_resourcehost_to_idlemodule/',
            description=u'资源池主机分配至业务的空闲机模块'
        )
        self.transfer_sethost_to_idle_module = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/transfer_sethost_to_idle_module/',
            description=u'清空业务下集群/模块中主机'
        )
        self.unsubcribe_event = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/unsubcribe_event/',
            description=u'退订事件'
        )
        self.update_business = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/update_business/',
            description=u'修改业务'
        )
        self.update_business_enable_status = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/update_business_enable_status/',
            description=u'修改业务启用状态'
        )
        self.update_classification = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/update_classification/',
            description=u'更新模型分类'
        )
        self.update_custom_query = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/update_custom_query/',
            description=u'更新自定义API'
        )
        self.update_event_subscribe = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/update_event_subscribe/',
            description=u'修改订阅'
        )
        self.update_host = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/update_host/',
            description=u'更新主机属性'
        )
        self.update_inst = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/update_inst/',
            description=u'更新对象实例'
        )
        self.update_module = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/update_module/',
            description=u'更新模块'
        )
        self.update_object = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/update_object/',
            description=u'更新定义'
        )
        self.update_object_attribute = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/update_object_attribute/',
            description=u'更新对象模型属性'
        )
        self.update_object_topo_graphics = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/update_object_topo_graphics/',
            description=u'更新拓扑图'
        )
        self.update_set = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/update_set/',
            description=u'更新集群'
        )
        self.update_user_group = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/update_user_group/',
            description=u'更新用户分组'
        )
        self.clone_host_property = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/clone_host_property/',
            description=u'克隆主机属性'
        )
        self.add_app = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/add_app/',
            description=u'新建业务'
        )
        self.add_module = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/add_module/',
            description=u'新建模块'
        )
        self.add_plat_id = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/add_plat_id/',
            description=u'新增子网ID'
        )
        self.add_set = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/add_set/',
            description=u'新建集群'
        )
        self.del_app = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/del_app/',
            description=u'删除业务'
        )
        self.del_host_in_app = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/del_host_in_app/',
            description=u'从业务空闲机集群中删除主机'
        )
        self.del_module = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/del_module/',
            description=u'删除模块'
        )
        self.del_plat = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/del_plat/',
            description=u'删除子网'
        )
        self.del_set = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/del_set/',
            description=u'删除集群'
        )
        self.del_set_host = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/del_set_host/',
            description=u'清空集群下所有主机'
        )
        self.edit_app = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/edit_app/',
            description=u'编辑业务'
        )
        self.enter_ip = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/enter_ip/',
            description=u'导入主机到业务'
        )
        self.get_app_agent_status = ComponentAPI(
            client=self.client, method='GET',
            path='/api/c/compapi{bk_api_ver}/cc/get_app_agent_status/',
            description=u'查询业务下Agent状态'
        )
        self.get_app_by_id = ComponentAPI(
            client=self.client, method='GET',
            path='/api/c/compapi{bk_api_ver}/cc/get_app_by_id/',
            description=u'查询业务信息'
        )
        self.get_app_by_user = ComponentAPI(
            client=self.client, method='GET',
            path='/api/c/compapi{bk_api_ver}/cc/get_app_by_user/',
            description=u'查询用户有权限的业务'
        )
        self.get_app_by_user_role = ComponentAPI(
            client=self.client, method='GET',
            path='/api/c/compapi{bk_api_ver}/cc/get_app_by_user_role/',
            description=u'根据用户角色查询用户业务'
        )
        self.get_app_host_list = ComponentAPI(
            client=self.client, method='GET',
            path='/api/c/compapi{bk_api_ver}/cc/get_app_host_list/',
            description=u'查询业务主机列表'
        )
        self.get_app_list = ComponentAPI(
            client=self.client, method='GET',
            path='/api/c/compapi{bk_api_ver}/cc/get_app_list/',
            description=u'查询业务列表'
        )
        self.get_host_by_company_id = ComponentAPI(
            client=self.client, method='GET',
            path='/api/c/compapi{bk_api_ver}/cc/get_host_by_company_id/',
            description=u'根据开发商ID、子网ID、主机IP获取主机信息'
        )
        self.get_host_company_id = ComponentAPI(
            client=self.client, method='GET',
            path='/api/c/compapi{bk_api_ver}/cc/get_host_company_id/',
            description=u'获取主机开发商'
        )
        self.get_host_list_by_field = ComponentAPI(
            client=self.client, method='GET',
            path='/api/c/compapi{bk_api_ver}/cc/get_host_list_by_field/',
            description=u'根据主机属性的值group主机列表'
        )
        self.get_host_list_by_ip = ComponentAPI(
            client=self.client, method='GET',
            path='/api/c/compapi{bk_api_ver}/cc/get_host_list_by_ip/',
            description=u'根据IP查询主机信息'
        )
        self.get_hosts_by_property = ComponentAPI(
            client=self.client, method='GET',
            path='/api/c/compapi{bk_api_ver}/cc/get_hosts_by_property/',
            description=u'根据 set 属性查询主机'
        )
        self.get_ip_and_proxy_by_company = ComponentAPI(
            client=self.client, method='GET',
            path='/api/c/compapi{bk_api_ver}/cc/get_ip_and_proxy_by_company/',
            description=u'查询业务下IP及ProxyIP'
        )
        self.get_module_host_list = ComponentAPI(
            client=self.client, method='GET',
            path='/api/c/compapi{bk_api_ver}/cc/get_module_host_list/',
            description=u'查询模块主机列表'
        )
        self.get_modules = ComponentAPI(
            client=self.client, method='GET',
            path='/api/c/compapi{bk_api_ver}/cc/get_modules/',
            description=u'查询业务下的所有模块'
        )
        self.get_modules_by_property = ComponentAPI(
            client=self.client, method='GET',
            path='/api/c/compapi{bk_api_ver}/cc/get_modules_by_property/',
            description=u'根据 set 属性查询模块'
        )
        self.get_plat_id = ComponentAPI(
            client=self.client, method='GET',
            path='/api/c/compapi{bk_api_ver}/cc/get_plat_id/',
            description=u'查询子网列表'
        )
        self.get_proc_config_instance_status = ComponentAPI(
            client=self.client, method='GET',
            path='/api/c/compapi{bk_api_ver}/cc/get_proc_config_instance_status/',
            description=u'获取刷新进程实例状态'
        )
        self.get_process_port_by_app_id = ComponentAPI(
            client=self.client, method='GET',
            path='/api/c/compapi{bk_api_ver}/cc/get_process_port_by_app_id/',
            description=u'查询进程端口'
        )
        self.get_property_list = ComponentAPI(
            client=self.client, method='GET',
            path='/api/c/compapi{bk_api_ver}/cc/get_property_list/',
            description=u'查询属性列表'
        )
        self.get_set_host_list = ComponentAPI(
            client=self.client, method='GET',
            path='/api/c/compapi{bk_api_ver}/cc/get_set_host_list/',
            description=u'查询Set主机列表'
        )
        self.get_set_property = ComponentAPI(
            client=self.client, method='GET',
            path='/api/c/compapi{bk_api_ver}/cc/get_set_property/',
            description=u'获取所有 set 属性'
        )
        self.get_sets_by_property = ComponentAPI(
            client=self.client, method='GET',
            path='/api/c/compapi{bk_api_ver}/cc/get_sets_by_property/',
            description=u'根据 set 属性获取 set'
        )
        self.get_topo_tree_by_app_id = ComponentAPI(
            client=self.client, method='GET',
            path='/api/c/compapi{bk_api_ver}/cc/get_topo_tree_by_app_id/',
            description=u'查询业务拓扑树'
        )
        self.update_custom_property = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/update_custom_property/',
            description=u'修改主机自定义属性'
        )
        self.update_gse_proxy_status = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/update_gse_proxy_status/',
            description=u'更新主机gse agent proxy 状态'
        )
        self.update_host_by_app_id = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/update_host_by_app_id/',
            description=u'更新主机的gse agent状态'
        )
        self.update_host_info = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/update_host_info/',
            description=u'更新主机属性'
        )
        self.update_host_module = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/update_host_module/',
            description=u'修改主机模块'
        )
        self.update_host_plat = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/update_host_plat/',
            description=u'更新主机云子网'
        )
        self.update_module_property = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/update_module_property/',
            description=u'修改模块属性'
        )
        self.update_proc_config_instance = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/update_proc_config_instance/',
            description=u'刷新进程配置实例'
        )
        self.update_set_property = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/update_set_property/',
            description=u'更新集群属性'
        )
        self.update_set_service_status = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/cc/update_set_service_status/',
            description=u'修改集群服务状态'
        )

        self.get_biz_internal_module = ComponentAPI(
            client=self.client, method='GET',
            path='/api/c/compapi{bk_api_ver}/cc/get_biz_internal_module/',
            description=u'获取业务空闲机和故障机模块'
        )
        self.get_mainline_object_topo = ComponentAPI(
            client=self.client, method='GET',
            path='/api/c/compapi{bk_api_ver}/cc/get_mainline_object_topo/',
            description=u'获取主线模型的业务拓扑'
        )

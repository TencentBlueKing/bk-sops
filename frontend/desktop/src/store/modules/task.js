/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
import axios from 'axios'
import store from '@/store/index.js'

const task = {
    namespaced: true,
    actions: {
        /**
         * 获取任务可选节点的选择方案
         * @param {Object} data 筛选条件
         */
        loadTaskScheme ({ commit }, payload) {
            const { isCommon, project_id, template_id } = payload
            const params = { template_id }
            if (isCommon) {
                params.template_type = 'common'
            } else {
                params.project_id = project_id
            }
            return axios.get('api/v3/scheme/', { params }).then(response => {
                const data = response.data.data
                return data
            })
        },
        /**
         * 创建任务可选节点的选择方案
         * @param {Object}} payload 方案配置数据
         */
        createTaskScheme ({ commit }, payload) {
            const { isCommon, project_id, template_id, data, name } = payload
            const params = {
                template_id,
                data,
                name
            }
            if (isCommon) {
                params.template_type = 'common'
            } else {
                params.project_id = project_id
            }
            return axios.post('api/v3/scheme/', params).then(response => response.data)
        },
        /**
         * 删除任务节点选择方案
         * @param {String} payload 方案参数
         */
        deleteTaskScheme ({ commit }, payload) {
            const { isCommon, id } = payload
            const params = {}
            if (isCommon) {
                params.template_type = 'common'
            }

            return axios.delete(`api/v3/scheme/${id}/`, { params }).then(response => response.data)
        },
        /**
         * 获取任务节点选择方案详情
         * @param {String} payload 方案参数
         */
        getSchemeDetail ({ commit }, payload) {
            const { isCommon, id } = payload
            const params = {}
            if (isCommon) {
                params.template_type = 'common'
            }

            return axios.get(`api/v3/scheme/${id}/`, { params }).then(response => response.data.data)
        },
        /**
         * 保存所有执行方案
         * @param {String} payload 方案参数
         */
        saveTaskSchemList ({ commit }, payload) {
            const { project_id, template_id, schemes, isCommon } = payload
            const params = {
                template_id,
                schemes
            }
            if (isCommon) {
                params.template_type = 'common'
            } else {
                params.project_id = project_id
            }
            return axios.post('api/v3/scheme/batch_operate/', params).then(response => response.data)
        },
        /**
         * 获取默认执行方案列表
         * @param {String} payload 方案参数
         */
        getDefaultTaskScheme ({ commit }, payload) {
            const { project_id, template_id, template_type } = payload
            const params = {
                template_id,
                project_id,
                template_type
            }
            return axios.get('template/api/default_scheme/', { params }).then(response => response.data)
        },
        /**
         * 保存默认执行方案列表
         * @param {String} payload 方案参数
         */
        saveDefaultScheme ({ commit }, payload) {
            const { project_id, template_id, scheme_ids, template_type } = payload
            const params = {
                template_id,
                project_id,
                template_type,
                scheme_ids
            }
            return axios.post('template/api/default_scheme/', params).then(response => response.data)
        },
        /**
         * 更新默认执行方案列表
         * @param {String} payload 方案参数
         */
        updateDefaultScheme ({ commit }, payload) {
            const { project_id, template_id, scheme_ids, id, template_type } = payload
            const params = {
                template_id,
                project_id,
                template_type,
                scheme_ids
            }
            return axios.put(`template/api/default_scheme/${id}/`, params).then(response => response.data)
        },
        /**
         * 删除默认执行方案列表
         * @param {String} payload 方案参数
         */
        deleteDefaultScheme ({ commit }, payload) {
            const { id } = payload
            return axios.delete(`template/api/default_scheme/${id}/`).then(response => response.data)
        },
        /**
         * 加载子流程详情
         * @param {String} data.projectId 项目id
         * @param {String} data.templateId 流程id
         * @param {String} data.version 流程版本
         * @param {String} data.common 是否为公共流程
         * @param {Array} data.scheme_id_list 执行方案列表
         */
        loadSubflowConfig ({ commit }, data) {
            return axios.post('/taskflow/api/preview_task_tree_with_schemes/', data).then(response => response.data)
        },
        /**
         * 获取任务节点预览数据
         * @param {Object} payload 筛选条件
         */
        loadPreviewNodeData ({ commit }, payload) {
            const { project_id } = store.state.project
            const { templateId, excludeTaskNodesId, common, version } = payload
            const dataJson = {
                version,
                template_id: templateId,
                exclude_task_nodes_id: excludeTaskNodesId,
                template_source: 'project'
            }
            if (common) {
                dataJson.template_source = 'common'
            }

            return axios.post(`taskflow/api/preview_task_tree/${project_id}/`, dataJson).then(response => response.data)
        },
        /**
         * 资源筛选配置方案全量列表
         * @param {String} payload 资源类型
         */
        configProgramList ({ commit }, payload) {
            const { project_id } = store.state.project
            return axios.get(`api/v3/resource_config/?project_id=${project_id}&config_type=${payload}`).then(response => response.data)
        },
        /**
         * 保存筛选方案
         * @param {String} params 项目信息数据
         */
        saveResourceScheme ({ commit }, params) {
            const { url, data } = params
            return axios.patch(url, data).then(response => response.data)
        },
        createResourceScheme ({ commit }, params) {
            const { url, data } = params
            return axios.post(url, data).then(response => response.data)
        },
        /**
         * 创建任务
         * @param {Object} data 模板数据
         */
        createTask ({ commit }, data) {
            const { app_id, view_mode, username } = store.state
            const { project_id } = store.state.project
            const { templateId, name, description, execData, flowType, common } = data
            const requestData = {
                name,
                description,
                'project': project_id,
                'template': templateId,
                'creator': username,
                'pipeline_tree': execData,
                'create_method': view_mode === 'appmaker' ? 'app_maker' : 'app',
                'create_info': app_id,
                'flow_type': flowType,
                'template_source': 'project'
            }
            if (common) {
                requestData.template_source = 'common'
            }

            return axios.post('api/v3/taskflow/', requestData).then(response => response.data.data)
        },
        /**
         * 获取任务实例详细数据
         * @param {String} instance_id 实例id
         */
        getTaskInstanceData ({ commit }, instance_id) {
            return axios.get(`api/v3/taskflow/${instance_id}/`).then(response => response.data.data)
        },
        /**
         * 职能化认领
         * @param {String} data 模板数据
         */
        claimFuncTask ({ commit }, data) {
            const { name, instance_id, constants, project_id } = data
            const requestData = {
                name,
                instance_id,
                constants
            }
            return axios.post(`taskflow/api/flow/claim/${project_id}/`, requestData).then(response => response.data)
        },
        /**
         * 获取任务执行状态
         * @param {Object} 实例数据
         * @returns Object
         */
        getTaskStatus ({ commit }, data) {
            const { instance_id, project_id } = data
            return axios.get(`taskflow/api/v4/root_state/${project_id}/`, {
                params: {
                    instance_id
                }
            }).then(response => response.data)
        },
        /**
         * 获取任务实例状态信息(包含子流程状态)
         * @param {String} data 实例数据
         */
        getInstanceStatus ({ commit }, data) {
            const { instance_id, project_id, subprocess_id, cancelToken } = data
            return axios.get(`taskflow/api/status/${project_id}/`, {
                params: {
                    instance_id,
                    subprocess_id
                }
            }, { cancelToken }).then(response => response.data)
        },
        /**
         * 开始执行任务实例
         * @param {String} instance_id 实例id
         */
        instanceStart ({ commit }, instance_id) {
            const { project_id } = store.state.project
            return axios.post(`taskflow/api/action/start/${project_id}/`, { instance_id }).then(response => response.data)
        },
        /**
         * 暂停执行任务实例
         * @param {String} instance_id 实例id
         */
        instancePause ({ commit }, instance_id) {
            const { project_id } = store.state.project
            return axios.post(`taskflow/api/action/pause/${project_id}/`, { instance_id }).then(response => response.data)
        },
        /**
         * 继续执行任务实例
         * @param {String} instance_id 实例id
         */
        instanceResume ({ commit }, instance_id) {
            const { project_id } = store.state.project
            return axios.post(`taskflow/api/action/resume/${project_id}/`, { instance_id }).then(response => response.data)
        },
        /**
         * 撤销任务实例执行
         * @param {String} instance_id 任务实例id
         */
        instanceRevoke ({ commit }, instance_id) {
            const { project_id } = store.state.project
            return axios.post(`taskflow/api/action/revoke/${project_id}/`, { instance_id }).then(response => response.data)
        },
        /**
         * 暂停子流程任务
         * @param {Object} data 子任务数据
         */
        subInstancePause ({ commit }, data) {
            const { instance_id, node_id } = data
            const { project_id } = store.state.project
            const qsData = { instance_id, node_id }
            return axios.post(`taskflow/api/nodes/action/pause_subproc/${project_id}/`, qsData).then(response => response.data)
        },
        /**
         * 继续子流程任务
         * @param {Object} data 子任务数据
         */
        subInstanceResume ({ commit }, data) {
            const { instance_id, node_id } = data
            const { project_id } = store.state.project
            const qsData = { instance_id, node_id }
            return axios.post(`taskflow/api/nodes/action/resume_subproc/${project_id}/`, qsData).then(response => response.data)
        },
        /**
         * 修改实例参数
         * @param {Object} data 表单配置数据
         */
        instanceModifyParams ({ commit }, data) {
            return axios.post(`taskflow/api/update_task_constants/${data.instance_id}/`, data).then(response => response.data)
        },
        /**
         * 获取节点执行详情
         * @param {Object} data 节点配置数据
         */
        getNodeActDetail ({ commit }, data) {
            const { project_id } = store.state.project
            const { instance_id, node_id, component_code, subprocess_stack, loop } = data
            return axios.get(`taskflow/api/nodes/detail/${project_id}/`, {
                params: {
                    instance_id,
                    node_id,
                    component_code,
                    subprocess_stack,
                    loop
                }
            }).then(response => response.data)
        },
        /**
         * 获取任务所有全局变量当前渲染后的值
         * @param {Object} data 节点配置数据
         */
        getRenderCurConstants ({ commit }, data) {
            const { task_id } = data
            return axios.get(`taskflow/api/render_current_constants/${task_id}/`).then(response => response.data)
        },
        /**
         * 获取模版操作记录
         * @param {Object} data 节点配置数据
         */
        getOperationRecordTemplate ({ commit }, data) {
            const { project_id, instance_id } = data
            return axios.get(`/api/v3/operate_record_template/`, {
                params: {
                    project_id,
                    instance_id
                }
            }).then(response => response.data)
        },
        /**
         * 获取任务操作记录
         * @param {Object} data 节点配置数据
         */
        getOperationRecordTask ({ commit }, data) {
            const { project_id, instance_id, node_id } = data
            return axios.get(`/api/v3/operate_record_task/`, {
                params: {
                    project_id,
                    instance_id,
                    node_id
                }
            }).then(response => response.data)
        },
        /**
         * 获取执行记录日志
         * @param {Object} data 节点配置数据
         */
        getNodeExecutionRecordLog ({ commit }, data) {
            const { project_id } = store.state.project
            const { history_id, instance_id, node_id, page = 1, page_size = 30 } = data
            return axios.get(`taskflow/api/nodes/log/${project_id}/${node_id}/`, {
                params: {
                    page,
                    page_size,
                    history_id,
                    instance_id
                }
            }).then(response => response.data)
        },
        // 获取v2引擎的节点日志
        getEngineVerNodeLog ({ commit }, data) {
            const { project_id } = store.state.project
            const { node_id, version, instance_id: task_id, page = 1, page_size = 30 } = data
            return axios.get(`taskflow/api/engine_v2/node_log/${project_id}/${task_id}/${node_id}/${version}/`, {
                params: {
                    page,
                    page_size
                }
            }).then(response => response.data)
        },
        /**
         * 获取节点执行信息
         * @param {Object} data 节点配置数据
         */
        getNodeActInfo ({ commit }, data) {
            const { project_id } = store.state.project
            const { instance_id, node_id, component_code, subprocess_stack } = data
            return axios.get(`taskflow/api/nodes/data/${project_id}/`, {
                params: {
                    instance_id,
                    node_id,
                    component_code,
                    subprocess_stack
                }
            }).then(response => response.data)
        },
        /**
         * 节点强制失败
         * @param {Object} data 任务实例数据
         */
        forceFail ({ commit }, data) {
            const { project_id } = store.state.project
            const { node_id, task_id } = data
            const action = 'forced_fail'
            return axios.post(`taskflow/api/v4/node_action/${project_id}/${task_id}/${node_id}/`, { action }, {
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
            }).then(response => response.data)
        },
        /**
         * 重试任务节点
         * @param {Object} data 任务实例数据
         */
        instanceRetry ({ commit }, data) {
            const { project_id } = store.state.project
            return axios.post(`taskflow/api/nodes/action/retry/${project_id}/`, data).then(response => response.data)
        },
        /**
         * 设置定时间节点时间
         * @param {Object} data 节点配置数据
         */
        setSleepNode ({ commit }, data) {
            const { project_id } = store.state.project
            return axios.post(`taskflow/api/nodes/spec/timer/reset/${project_id}/`, data).then(response => response.data)
        },
        /**
         * 跳过失败节点
         * @param {Object} data 节点配置数据
         */
        instanceNodeSkip ({ commit }, data) {
            const { project_id } = store.state.project
            return axios.post(`taskflow/api/nodes/action/skip/${project_id}/`, data).then(response => response.data)
        },
        /**
         * 跳过分支网关节点
         * @param {Object} data 节点配置数据
         */
        skipExclusiveGateway ({ commit }, data) {
            const { project_id } = store.state.project
            return axios.post(`taskflow/api/nodes/action/skip_exg/${project_id}/`, data).then(response => response.data)
        },
        /**
         * 跳过条件并行网关节点
         * @param {Object} data 节点配置数据
         */
        skipCondParallelGateWay ({ commit }, data) {
            const { project_id } = store.state.project
            return axios.post(`taskflow/api/nodes/action/skip_cpg/${project_id}/`, data).then(response => response.data)
        },
        /**
         * 暂停节点继续
         * @param {Object} data 节点配置数据
         */
        pauseNodeResume ({ commit }, data) {
            const { project_id } = store.state.project
            return axios.post(`taskflow/api/nodes/action/callback/${project_id}/`, data).then(response => response.data)
        },
        // 加载创建任务方式数据
        loadCreateMethod () {
            return axios.get('taskflow/api/get_task_create_method/').then(response => response.data)
        },
        /**
         * 获取作业执行详情
         * @param {Object} data 作业实例ID等信息
         */
        getJobInstanceLog ({ commit }, data) {
            const { job_instance_id, project_id } = data
            return axios.get(`taskflow/api/nodes/get_job_instance_log/${project_id}/`, {
                params: { job_instance_id }
            }).then(response => response.data)
        },
        subflowNodeRetry ({ commit }, data) {
            const { project_id } = store.state.project
            return axios.post(`taskflow/api/nodes/action/retry_subprocess/${project_id}/`, data).then(response => response.data)
        },
        // itsm 节点审批
        itsmTransition ({ commit }, params) {
            return axios.post('pipeline/itsm/node_transition/', params).then(response => response.data)
        },
        getInstanceRetryParams ({ commit }, data) {
            return axios.get(`api/v3/taskflow/${data.id}/enable_fill_retry_params/`).then(response => response.data)
        },
        // 节点执行记录
        getNodeExecutionRecord ({ commit }, data) {
            return axios.get(`api/v3/taskflow/node_execution_record/`, {
                params: {
                    template_node_id: data.tempNodeId
                }
            }).then(response => response.data)
        }
    }
}

export default task

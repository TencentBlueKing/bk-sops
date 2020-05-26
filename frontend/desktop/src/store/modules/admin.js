/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
import axios from 'axios'

const admin = {
    namespaced: true,
    actions: {
        // 管理员搜索返回匹配结果
        search ({ commit }, data) {
            return axios.post('admin/search/', { keyword: data.keyword }).then(response => response.data)
        },
        // 管理员搜索模板列表
        template ({ commit }, data) {
            return axios.get('admin/api/v3/template/', {
                params: { ...data }
            }).then(response => response.data)
        },
        // 管理员搜索任务列表
        taskflow ({ commit }, data) {
            return axios.get('admin/api/v3/taskflow/', {
                params: { ...data }
            }).then(response => response.data)
        },
        // 周期任务启动记录
        periodTaskHistory ({ commit }, data) {
            const { task_id } = data
            return axios.get('admin/api/v3/periodic_task_history/', {
                params: { task_id }
            }).then(response => response.data)
        },
        // 恢复模板
        templateRestore ({ commit }, data) {
            const { template_id } = data
            return axios.post('admin/template/restore/', { template_id }).then(response => response.data)
        },
        // 任务执行详情，管理员入口进入
        taskflowDetail ({ commit }, data) {
            const { task_id } = data
            return axios.get('admin/taskflow/detail/', {
                params: { task_id }
            }).then(response => response.data)
        },
        // 节点执行详情，管理员入口进入
        taskflowNodeDetail ({ commit }, data) {
            return axios.get('admin/taskflow/node/detail/', {
                params: { ...data }
            }).then(response => response.data)
        },
        // 节点执行历史记录，管理员入口进入
        taskflowHistroyLog ({ commit }, data) {
            return axios.get('admin/taskflow/node/history/log/', {
                params: { ...data }
            }).then(response => response.data)
        },
        // 节点强制失败，管理员入口进入
        taskflowNodeForceFail ({ commit }, data) {
            const { task_id, node_id } = data
            return axios.post('admin/taskflow/node/force_fail/', { task_id, node_id }).then(response => response.data)
        },
        // 加载标准插件统计数据
        queryTemplateData ({ commit }, data) {
            return axios.post('analysis/query_template_by_group/', data).then(response => response.data)
        },
        // 加载标准插件统计数据
        queryAtomData ({ commit }, data) {
            return axios.post('analysis/query_atom_by_group/', data).then(response => response.data)
        },
        // 加载任务实例统计数据
        queryInstanceData ({ commit }, data) {
            return axios.post('analysis/query_instance_by_group/', data).then(response => response.data)
        },
        // 加载轻应用统计数据
        queryAppmakerData ({ commit }, data) {
            return axios.post('analysis/query_appmaker_by_group/', data).then(response => response.data)
        }
    }
}

export default admin

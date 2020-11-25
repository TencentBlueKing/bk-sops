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
import store from '@/store/index.js'

const periodic = {
    namespaced: true,
    mutations: {},
    actions: {
        // 获取周期任务列表
        loadPeriodicList ({ commit }, data) {
            return axios.get('api/v3/periodic_task/', {
                params: { ...data }
            }).then(response => response.data)
        },
        /**
         * 创建定时任务
         * @param {Object} data 包含 template_id模板名称, name定时名称, cron定时表达式
         */
        createPeriodic ({ state }, data) {
            const { project_id } = store.state.project
            const { name, cron, templateId, execData, templateSource } = data

            return axios.post('api/v3/periodic_task/', {
                project: `api/v3/project/${project_id}/`,
                cron,
                name,
                template_id: templateId,
                pipeline_tree: execData,
                template_source: templateSource
            }).then(response => response.data)
        },
        /**
         * 设置定时任务执行状态
         * @param {Object} data task_id 定时任务id, enabled 需要切换的状态
         */
        setPeriodicEnable ({ commit }, data) {
            const { project_id } = store.state.project
            const { enabled, taskId } = data

            return axios.post(`periodictask/api/enabled/${project_id}/${taskId}/`, { enabled }).then(response => response.data)
        },
        /**
         * 修改定时任务表达式
         * @param {Object} data task_id 定时任务id, cron 表达式
         */
        modifyPeriodicCron ({ commit }, data) {
            const { project_id } = store.state.project
            const { cron, taskId } = data
            return axios.post(`periodictask/api/cron/${project_id}/${taskId}/`, { cron }).then(response => response.data)
        },
        // 获取周期任务详情
        getPeriodic ({ commit }, data) {
            const { project_id } = store.state.project
            const { taskId } = data
            const querystring = Object.assign({}, { 'project_id': project_id })
            return axios.get(`api/v3/periodic_task/${taskId}/`, {
                params: querystring
            }).then(response => response.data)
        },
        // 修改周期任务参数信息
        modifyPeriodicConstants ({ commit }, data) {
            const { project_id } = store.state.project
            const { constants, taskId } = data
            return axios.post(`periodictask/api/constants/${project_id}/${taskId}/`, { constants }).then(response => response.data)
        },
        // 删除单个周期任务
        deletePeriodic ({ commit }, taskId) {
            return axios.delete(`api/v3/periodic_task/${taskId}/`).then(response => response.data)
        }
    }
}

export default periodic

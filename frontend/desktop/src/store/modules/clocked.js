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

const clocked = {
    namespaced: true,
    mutations: {},
    actions: {
        /**
         * 获取计划任务列表
         * @param {Object} data 所需参数
         */
        loadClockedList ({ state }, data) {
            const { params, config = {} } = data
            return axios.get('api/v4/clocked_task/', { params, ...config }).then(response => response.data)
        },
        /**
         * 获取计划任务详情
         * @param {Object} data 所需参数
         */
        getClockedDetail ({ state }, data) {
            return axios.get(`api/v4/clocked_task/${data.id}/`).then(response => response.data)
        },
        /**
         * 创建计划任务
         * @param {Object} data 所需参数
         */
        createClocked ({ state }, data) {
            const { project_id } = store.state.project
            return axios.post('api/v4/clocked_task/', {
                project_id,
                ...data
            }).then(response => response.data)
        },
        /**
         * 更新计划任务
         * @param {Object} data 所需参数
         */
        updateClocked ({ state }, data) {
            const { id, task_parameters, plan_start_time, task_name } = data

            return axios.patch(`api/v4/clocked_task/${id}/`, {
                task_name,
                task_parameters,
                plan_start_time
            }).then(response => response.data)
        },
        /**
         * 删除计划任务
         * @param {Object} data 所需参数
         */
        deleteClocked ({ state }, data) {
            return axios.delete(`api/v4/clocked_task/${data.id}/`).then(response => response.data)
        }
    }
}

export default clocked

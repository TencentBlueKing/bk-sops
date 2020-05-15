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
import api from '@/api/index.js'

const admin = {
    namespaced: true,
    state: {},
    mutations: {},
    actions: {
        search ({ commit }, data) {
            return api.adminSearch(data).then(
                response => response.data
            )
        },
        template ({ commit }, data) {
            return api.adminTemplate(data).then(
                response => response.data
            )
        },
        taskflow ({ commit }, data) {
            return api.adminTaskflow(data).then(
                response => response.data
            )
        },
        periodTask ({ commit }, data) {
            return api.adminPeriodTask(data).then(
                response => response.data
            )
        },
        periodTaskHistory ({ commit }, data) {
            return api.adminPeriodTaskHistory(data).then(
                response => response.data
            )
        },
        templateRestore ({ commit }, data) {
            return api.adminTemplateRestore(data).then(
                response => response.data
            )
        },
        taskflowDetail ({ commit }, data) {
            return api.adminTaskflowDetail(data).then(
                response => response.data
            )
        },
        taskflowNodeDetail ({ commit }, data) {
            return api.adminTaskflowNodeDetail(data).then(
                response => response.data
            )
        },
        taskflowHistroyLog ({ commit }, data) {
            return api.adminTaskflowHistroyLog(data).then(
                response => response.data
            )
        },
        taskflowNodeForceFail ({ commit }, data) {
            return api.adminTaskflowNodeForceFail(data).then(
                response => response.data
            )
        }
    }
}

export default admin

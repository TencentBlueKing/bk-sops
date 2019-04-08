/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
import api from "@/api/index.js"
import tools from '@/utils/tools.js'

const periodic = {
    namespaced: true,
    mutations: {
    },
    actions: {
        loadPeriodicList ({commit}, data) {
            return api.getPeriodicList(data).then(response => response.data)
        },
        createPeriodic ({state},data) {
            return api.createPeriodic(data).then(response => response.data)
        },
        setPeriodicEnable ({commit}, data) {
            return api.setPeriodicEnable(data).then(response => response.data)
        },
        modifyPeriodicCron ({commit}, data) {
            return api.modifyPeriodicCron(data).then(response => response.data)
        },
        getPeriodic ({commit}, data) {
            return api.getPeriodic(data).then(response => response.data)
        },
        modifyPeriodicConstants ({commit}, data) {
            return api.modifyPeriodicConstants(data).then(response => response.data)
        },
        deletePeriodic ({commit}, taskId) {
            return api.deletePeriodic(taskId).then(response => response.data)
        }
    },
    getters: {}
}

export default periodic
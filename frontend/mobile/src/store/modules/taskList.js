/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
import http from '@/api'

export default {
    namespaced: true,
    state: {},
    mutations: {},
    actions: {
        getTaskStatus ({ commit, rootState }, params) {
            const url = `${global.getMobileUrlPrefix(rootState.bizId).instanceStatus}?instance_id=${params.id}`
            return http.get(url).then(response => {
                return response.result ? response.data : {}
            })
        },

        getTaskList ({ commit, rootState, dispatch }, params) {
            const url = `${global.getMobileUrlPrefix().instance}?limit=${params.limit}&offset=${params.offset}&create_method=mobile`
            return http.get(url).then(response => response)
        }
    }
}

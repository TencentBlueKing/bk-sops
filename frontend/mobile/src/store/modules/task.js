/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
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
        getTask ({ commit } = {}, params) {
            return http.get(`api/v3/weixin_taskflow/${params.id}/`).then(response => response.data)
        },

        getTaskStatus ({ commit, rootState }, params) {
            return http.get(`taskflow/api/status/${rootState.bizId}/`, { params: { instance_id: params.id } }).then(response => response)
        },

        instanceStart ({ commit, rootState }, params) {
            const data = { instance_id: params.id }
            return http.post(`taskflow/api/action/start/${rootState.bizId}/`, data).then(response => response)
        },

        instanceRevoke ({ commit, rootState }, params) {
            const data = { instance_id: params.id }
            return http.post(`taskflow/api/action/revoke/${rootState.bizId}/`, data).then(response => response)
        },

        instancePause ({ commit, rootState }, params) {
            const data = { instance_id: params.id }
            return http.post(`taskflow/api/action/pause/${rootState.bizId}/`, data).then(response => response)
        },

        instanceResume ({ commit, rootState }, params) {
            const data = { instance_id: params.id }
            return http.post(`taskflow/api/action/resume/${rootState.bizId}/`, data).then(response => response)
        },

        instanceNodeSkip ({ commit, rootState }, params) {
            const data = { instance_id: params.id, node_id: params.nodeId }
            return http.post(`taskflow/api/nodes/action/skip/${rootState.bizId}/`, data).then(response => response)
        },

        instanceNodeRetry ({ commit, rootState }, params) {
            return http.post(`taskflow/api/nodes/action/retry/${rootState.bizId}/`, params).then(response => response)
        },

        instanceNodeResume ({ commit, rootState }, params) {
            const data = params
            data.data = { callback: 'resume' }
            return http.post(`taskflow/api/nodes/action/callback/${rootState.bizId}/`, data).then(response => response)
        },

        instanceNodeEditTime ({ commit, rootState }, params) {
            return http.post(`taskflow/api/nodes/spec/timer/reset/${rootState.bizId}/`, params).then(response => response)
        },

        getNodeDetail ({ rootState }, params) {
            return http.get(`taskflow/api/nodes/detail/${rootState.bizId}/`, {
                params: {
                    instance_id: params.taskId,
                    node_id: params.nodeId,
                    component_code: params.componentCode,
                    subprocess_stack: '[]'
                }
            }).then(response => response)
        },

        getNodeRetryData ({ rootState }, params) {
            return http.get(`taskflow/api/nodes/data/${rootState.bizId}/`, {
                params: {
                    instance_id: params.taskId,
                    node_id: params.nodeId,
                    component_code: params.componentCode,
                    subprocess_stack: '[]'
                }
            }).then(response => response)
        }
    }
}

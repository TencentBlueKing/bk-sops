/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
import http from '@/api'
import qs from 'qs'

export default {
    namespaced: true,
    state: {},
    mutations: {},
    actions: {
        getTask ({ commit, state, dispatch } = {}, params) {
            const url = `${global.getMobileUrlPrefix().instance}${params.id}/`
            return http.get(url).then(response => response)
        },

        getTaskStatus ({ commit, rootState }, params) {
            const url = `${global.getMobileUrlPrefix(rootState.bizId).instanceStatus}?instance_id=${params.id}`
            return http.get(url).then(response => response)
        },

        instanceStart ({ commit, rootState }, params) {
            const data = qs.stringify({ instance_id: params.id })
            const url = `${global.getMobileUrlPrefix(rootState.bizId).instanceStart}?instance_id=${params.id}`
            return http.post(url, data, { headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest' } }).then(response => response)
        },

        instanceRevoke ({ commit, rootState }, params) {
            const data = qs.stringify({ instance_id: params.id })
            const url = `${global.getMobileUrlPrefix(rootState.bizId).instanceRevoke}`
            return http.post(url, data, { headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest' } }).then(response => response)
        },

        instancePause ({ commit, rootState }, params) {
            const data = qs.stringify({ instance_id: params.id })
            const url = `${global.getMobileUrlPrefix(rootState.bizId).instancePause}`
            return http.post(url, data, { headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest' } }).then(response => response)
        },

        instanceResume ({ commit, rootState }, params) {
            const data = qs.stringify({ instance_id: params.id })
            const url = `${global.getMobileUrlPrefix(rootState.bizId).instanceResume}`
            return http.post(url, data, { headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest' } }).then(response => response)
        },

        instanceNodeSkip ({ commit, rootState }, params) {
            const data = qs.stringify({ instance_id: params.id, node_id: params.nodeId })
            const url = `${global.getMobileUrlPrefix(rootState.bizId).nodeSkip}`
            return http.post(url, data, { headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest' } }).then(response => response)
        },

        instanceNodeRetry ({ commit, rootState }, params) {
            const data = qs.stringify(params)
            const url = `${global.getMobileUrlPrefix(rootState.bizId).nodeRetry}`
            return http.post(url, data, { headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest' } }).then(response => response)
        },

        instanceNodeResume ({ commit, rootState }, params) {
            params.data = { callback: 'resume' }
            const data = qs.stringify(params)
            const url = `${global.getMobileUrlPrefix(rootState.bizId).pauseNodeResume}`
            return http.post(url, data, { headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest' } }).then(response => response)
        },

        instanceNodeEditTime ({ commit, rootState }, params) {
            const data = qs.stringify(params)
            const url = `${global.getMobileUrlPrefix(rootState.bizId).setSleepNode}`
            return http.post(url, data, { headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest' } }).then(response => response)
        },

        getNodeDetail ({ rootState }, params) {
            const url = `${global.getMobileUrlPrefix(rootState.bizId).nodeActDetails}?instance_id=${params.taskId}&node_id=${params.nodeId}&component_code=${params.componentCode}&subprocess_stack=[]`
            return http.get(url).then(response => response)
        },

        getNodeRetryData ({ rootState }, params) {
            const url = `${global.getMobileUrlPrefix(rootState.bizId).nodeActInfo}?instance_id=${params.taskId}&node_id=${params.nodeId}&component_code=${params.componentCode}&subprocess_stack=[]`
            return http.get(url).then(response => response)
        }
    }
}

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
    state: {
        id: ''
    },
    mutations: {
        setTemplateId (state, id) {
            state.id = id
        }
    },
    actions: {
        getTemplateList ({ rootState }, { limit, offset = 0 } = {}) {
            const pager = limit ? `limit=${limit}&offset=${offset}&` : ''
            const url = `${global.getMobileUrlPrefix().template}?${pager}business__cc_id=${rootState.bizId}`
            return http.get(url).then(response => response)
        },

        getTemplate ({ commit, state }, templateId) {
            const url = `${global.getMobileUrlPrefix().template}${templateId}/`
            commit('setTemplateId', templateId)
            return http.get(url).then(response => response)
        },

        collectTemplate ({ rootState }, params) {
            const url = `${global.getMobileUrlPrefix(rootState.bizId).templateCollect}`
            return http.post(
                url,
                qs.stringify(params),
                { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }
            ).then(response => response)
        },

        getSchemeList ({ commit, state, rootState }) {
            const url = `${global.getMobileUrlPrefix().schemes}?biz_cc_id=${rootState.bizId}&template_id=${state.id}`
            return http.get(url).then(response => {
                const data = response.objects || []
                data.map(o => {
                    o.text = o.name
                    return o
                })
                return data
            })
        },

        getScheme ({ commit, state }, id) {
            const url = `${global.getMobileUrlPrefix().schemes}${id}/`
            return http.get(url).then(response => response)
        },

        getPreviewTaskTree ({ rootState }, params) {
            const url = `${global.getMobileUrlPrefix(rootState.bizId).instancePreview}`
            return http.post(
                url,
                qs.stringify(params),
                { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }
            ).then(response => {
                return response.data.pipeline_tree
            })
        },

        createTask ({ rootState, state }, data) {
            const url = `${global.getMobileUrlPrefix().instance}`
            const requestData = {
                'business': `api/v3/business/${rootState.bizId}/`,
                'template_id': state.id,
                'creator': rootState.user.username,
                'name': data.name,
                'description': data.description,
                'pipeline_tree': data.exec_data,
                'create_method': 'mobile',
                'create_info': 'mobile',
                'flow_type': 'common'
            }
            return http.post(
                url,
                requestData,
                { headers: { 'Content-Type': 'application/json;charset=UTF-8' } }
            ).then(response => response)
        }
    }
}

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
    state: {
        id: ''
    },
    mutations: {
        setTemplateId (state, id) {
            state.id = id
        }
    },
    actions: {
        getTemplateList ({ rootState }, params = {}) {
            const { limit, offset } = params
            return http.get('api/v3/weixin_template/', {
                params: { limit, offset, project__id: rootState.bizId }
            }).then(response => response)
        },
        getTemplate ({ commit, state }, templateId) {
            commit('setTemplateId', templateId)
            return http.get(`api/v3/weixin_template/${templateId}/`).then(response => response)
        },
        getCollectedTemplate ({ rootState }) {
            return http.get(`api/v3/weixin_collection/`).then(response => response)
        },
        collectTemplate ({ rootState }, list) {
            return http.put(
                `api/v3/weixin_collection/`,
                { objects: list }
            ).then(response => response)
        },
        deleteCollect ({ rootState }, id) {
            return http.delete(`api/v3/weixin_collection/${id}/`).then(response => response.data)
        },
        getSchemeList ({ state, rootState }) {
            return http.get('api/v3/weixin_scheme/', {
                params: {
                    project__id: rootState.bizId,
                    template_id: state.id
                }
            }).then((response) => {
                const data = response.objects || []
                data.map((o) => {
                    o.text = o.name
                    return o
                })
                return data
            })
        },
        getScheme ({ commit, state }, id) {
            return http.get(`api/v3/weixin_scheme/${id}/`).then(response => response)
        },
        getPreviewTaskTree ({ rootState }, data) {
            return http.post(`taskflow/api/preview_task_tree/${rootState.bizId}/`, data).then(response => response.data.pipeline_tree)
        },
        createTask ({ rootState, state }, data) {
            const requestData = {
                'project': `api/v3/project/${rootState.bizId}/`,
                'template_id': state.id,
                'creator': rootState.user.username,
                'name': data.name,
                'description': data.description,
                'pipeline_tree': JSON.stringify(data.exec_data),
                'create_method': 'mobile',
                'create_info': 'mobile',
                'flow_type': 'common',
                'template_source': 'project'
            }
            return http.post(
                'api/v3/weixin_taskflow/',
                requestData
            ).then(response => response)
        }
    }
}

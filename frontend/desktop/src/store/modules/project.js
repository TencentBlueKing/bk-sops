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
import axios from 'axios'

const SITE_URL = '/t/bk_sops/'

const project = {
    namespaced: true,
    state: {
        project_id: Number(window.DEFAULT_PROJECT_ID),
        projectName: '',
        projectList: [],
        timeZone: window.TIMEZONE,
        authResource: {},
        authOperations: [],
        authActions: []
    },
    mutations: {
        setProjectList (state, data) {
            state.projectList = data
        },
        setProjectId (state, data) {
            state.project_id = data
        },
        setTimeZone (state, data) {
            state.timeZone = data
        },
        setProjectName (state, data) {
            state.projectName = data
        },
        setProjectActions (state, data) {
            state.authActions = data
        },
        setProjectPerm (state, data) {
            state.authResource = data.auth_resource
            state.authOperations = data.auth_operations
        }
    },
    actions: {
        // 更改用户的默认项目
        changeDefaultProject ({ state }, data) {
            return axios.post(SITE_URL + `core/api/change_default_project/${state.project_id}/`).then(response => response.data)
        },
        loadProjectList ({ commit }, data) {
            const { limit, offset, is_disable = false, q } = data
            return axios.get(SITE_URL + `api/v3/project/`, {
                params: {
                    limit,
                    offset,
                    is_disable,
                    q
                }
            }).then(response => {
                if (data && data.limit === 0) {
                    commit('setProjectList', response.data.objects)
                }

                return response.data
            })
        },
        // 获取常用业务
        loadCommonProject ({ commit }, data) {
            return axios.get(SITE_URL + 'api/v3/common_use_project/').then(response => response.data)
        },
        createProject ({ commit }, data) {
            const { name, time_zone, desc } = data

            return axios.post(SITE_URL + `api/v3/project/`, {
                name,
                time_zone,
                desc
            }).then(response => response.data)
        },
        loadProjectDetail ({ commit }, id) {
            return axios.get(SITE_URL + `api/v3/project/${id}/`).then(
                response => response.data
            )
        },
        // 更新项目详情
        updateProject ({ commit }, data) {
            const { id, name, time_zone, desc, is_disable } = data
            return axios.patch(SITE_URL + `api/v3/project/${id}/`, {
                name,
                time_zone,
                desc,
                is_disable
            }).then(response => response.data)
        }
    },
    getters: {
        userCanViewProjects (state) {
            return state.projectList.filter(item => {
                return item.auth_actions.indexOf('view') > -1
            })
        }
    }
}

export default project

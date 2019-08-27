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
import api from '@/api/index.js'

const project = {
    namespaced: true,
    state: {
        project_id: window.DEFAULT_PROJECT_ID,
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
            state.projectName = data.name
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
        changeDefaultProject ({ commit }, data) {
            return api.changeDefaultProject(data).then(
                response => response.data
            )
        },
        loadProjectList ({ commit }, data) {
            return api.loadProjectList(data).then(response => {
                if (data && data.limit === 0) {
                    const authedList = response.data.objects.filter(item => item.auth_actions.indexOf('view') > -1)
                    commit('setProjectList', authedList)
                }
                
                return response.data
            })
        },
        createProject ({ commit }, data) {
            return api.createProject(data).then(
                response => response.data
            )
        },
        loadProjectDetail ({ commit }, id) {
            return api.loadProjectDetail(id).then(
                response => response.data
            )
        },
        updateProject ({ commit }, data) {
            return api.updateProject(data).then(
                response => response.data
            )
        }
    }
}

export default project

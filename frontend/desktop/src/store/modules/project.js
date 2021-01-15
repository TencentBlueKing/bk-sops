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
import axios from 'axios'

const project = {
    namespaced: true,
    state: {
        project_id: window.DEFAULT_PROJECT_ID,
        bizId: '',
        projectName: '',
        projectList: [],
        userProjectList: [], // 用户有权限的项目列表
        timeZone: window.TIMEZONE,
        authActions: []
    },
    mutations: {
        setProjectList (state, data) {
            state.projectList = data
        },
        setUserProjectList (state, data) {
            state.userProjectList = data
        },
        setProjectId (state, id) {
            if (typeof id !== 'number') {
                id = isNaN(Number(id)) || id === '' ? '' : Number(id)
            }
            state.project_id = id
        },
        setBizId (state, id) {
            state.bizId = id
        },
        setTimeZone (state, data) {
            state.timeZone = data
        },
        setProjectName (state, data) {
            state.projectName = data
        },
        setProjectActions (state, data) {
            state.authActions = data
        }
    },
    actions: {
        // 更改用户的默认项目
        changeDefaultProject ({ state }, id) {
            return axios.post(`core/api/change_default_project/${id}/`).then(response => response.data)
        },
        loadProjectList ({ commit }, data) {
            const { limit, offset, is_disable = false, q } = data
            return axios.get(`api/v3/project/`, {
                params: {
                    limit,
                    offset,
                    is_disable,
                    q
                }
            }).then(response => {
                return response.data
            })
        },
        // 加载用户有权限的项目列表
        loadUserProjectList ({ commit }, params) {
            return axios.get(`api/v3/user_project/`, { params }).then(response => {
                commit('setUserProjectList', response.data.objects)
                return response.data
            })
        },
        // 获取常用业务
        loadCommonProject ({ commit }, data) {
            return axios.get('api/v3/common_use_project/').then(response => response.data)
        },
        createProject ({ commit }, data) {
            const { name, time_zone, desc } = data

            return axios.post(`api/v3/project/`, {
                name,
                time_zone,
                desc
            }).then(response => response.data)
        },
        loadProjectDetail ({ commit }, id) {
            return axios.get(`api/v3/project/${id}/`).then(
                response => response.data
            )
        },
        // 更新项目详情
        updateProject ({ commit }, data) {
            const { id, name, time_zone, desc, is_disable } = data
            return axios.patch(`api/v3/project/${id}/`, {
                name,
                time_zone,
                desc,
                is_disable
            }).then(response => response.data)
        },
        getProjectConfig ({ commit }, id) {
            return axios.get(`api/v3/project_config/${id}/`).then(
                response => response.data
            )
        },
        updateProjectConfig ({ commit }, params) {
            const { id, executor_proxy, executor_proxy_exempts } = params
            return axios.patch(`api/v3/project_config/${id}/`, { executor_proxy, executor_proxy_exempts }).then(
                response => response.data
            )
        },
        getProjectStaffGroupList ({ commit }, params) {
            return axios.get(`api/v3/staff_group/`, { params }).then(
                response => response.data
            )
        },
        createProjectStaffGroup ({ commit }, params) {
            return axios.post(`api/v3/staff_group/`, params.data).then(
                response => response.data
            )
        },
        updateProjectStaffGroup ({ commit }, params) {
            const { id, data } = params
            return axios.put(`api/v3/staff_group/${id}/`, data).then(
                response => response.data
            )
        },
        delProjectStaffGroup ({ commit }, id) {
            return axios.delete(`api/v3/staff_group/${id}/`).then(
                response => response.data
            )
        },
        // 查询项目下用户可编辑的模板标签
        getProjectLabels ({ commit }, id) {
            return axios.get('api/v3/new_label/', {
                params: { project_id: id }
            }).then(response => response.data)
        },
        // 查询项目下支持的模板标签（包含默认标签）
        getProjectLabelsWithDefault ({ commit }, id) {
            return axios.get('api/v3/new_label/list_with_default_labels/', {
                params: { project_id: id }
            }).then(response => response.data)
        },
        createTemplateLabel ({ commit }, data) {
            return axios.post(`api/v3/new_label/`, data).then(
                response => response.data
            )
        },
        updateTemplateLabel ({ commit }, data) {
            return axios.put(`api/v3/new_label/${data.id}/`, data).then(
                response => response.data
            )
        },
        delTemplateLabel ({ commit }, id) {
            return axios.delete(`api/v3/new_label/${id}/`).then(
                response => response.data
            )
        },
        getlabelsCitedCount ({ commit }, ids) {
            return axios.get('api/v3/new_label/get_label_template_ids/', {
                params: { label_ids: ids }
            }).then(response => response.data)
        }
    }
}

export default project

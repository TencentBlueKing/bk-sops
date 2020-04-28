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
import store from '@/store/index.js'

const appmaker = {
    namespaced: true,
    state: {
        appmakerTemplateId: '', // 轻应用页面全局 template_id
        appmakerDetail: {
            auth_actions: [],
            auth_resource: {},
            auth_operations: [],
            id: '',
            name: ''
        }
    },
    mutations: {
        setAppmakerTemplateId (state, id) {
            state.appmakerTemplateId = id
        },
        setAppmakerDetail (state, data) {
            state.appmakerDetail = data
        }
    },
    actions: {
        // 加载轻应用列表
        loadAppmaker ({ commit }, data) {
            data.test = 6
            const querystring = Object.assign({}, data)
            return axios.get('api/v3/appmaker/', {
                params: querystring
            }).then(response => response.data)
        },
        /**
         * 加载对应轻应用详情
         * @param {String} id 轻应用id
         */
        loadAppmakerDetail ({ commit }, id) {
            return axios.get(`api/v3/appmaker/${id}/`, {
                params: { appmaker_id: id }
            }).then(response => response.data)
        },
        appmakerEdit ({ commit }, data) {
            const { project_id } = store.state.project
            return axios.post(`appmaker/save/${project_id}/`, data, {
                headers: { 'content-type': 'multipart/form-data' }
            }).then(response => response.data)
        },
        appmakerDelete ({ commit }, id) {
            return axios.delete(`api/v3/appmaker/${id}/`).then(response => response.data)
        }
    }
}

export default appmaker

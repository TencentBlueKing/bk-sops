/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
import api from '@/api/index.js'

const appmaker = {
    namespaced: true,
    state: {
    },
    mutations: {
    },
    actions: {
        loadAppmakerSummary () {
            return api.loadAppmakerSummary().then(response => response.data)
        },
        loadAppmakerDetail ({commit}, id) {
            return api.loadAppmakerDetail(id).then(response => response.data)
        },
        appmakerEdit ({commit}, data) {
            return api.appmakerEdit(data).then(response => response.data)
        },
        appmakerDelete ({commit}, id) {
            return api.appmakerDelete(id).then(response => response.data)
        },
        queryAppmakerData ({commit}, data) {
            return api.queryAppmaker(data).then(response => response.data)
        }
    }
}

export default appmaker